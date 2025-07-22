from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import desc, and_
import json
from datetime import datetime, timedelta

from ..models.database_models import Listing, AgentResult, ListingVersion, Project, ListingProject
from ..models import ProductInput, ProcessedListing, AgentResponse

class ListingService:
    """
    Servicio para gestionar listings en la base de datos
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_listing(
        self, 
        product_input: ProductInput, 
        processed_listing: ProcessedListing,
        agent_responses: Dict[str, AgentResponse],
        user_id: int
    ) -> Listing:
        """
        Crea un nuevo listing en la base de datos
        """
        # Crear el listing principal
        db_listing = Listing(
            product_name=product_input.product_name,
            category=str(product_input.category),
            target_price=product_input.target_price,
            input_data=product_input.dict(),
            title=processed_listing.title,
            bullet_points=processed_listing.bullet_points,
            description=processed_listing.description,
            search_terms=processed_listing.search_terms,
            backend_keywords=processed_listing.backend_keywords,
            images_order=processed_listing.images_order,
            image_ai_prompts=processed_listing.image_ai_prompts,
            a_plus_content=processed_listing.a_plus_content,
            confidence_score=processed_listing.confidence_score,
            processing_notes=processed_listing.processing_notes,
            recommendations=processed_listing.recommendations,
            status="draft",
            version=1,
            user_id=user_id
        )
        
        self.db.add(db_listing)
        await self.db.flush()  # Para obtener el ID
        
        # Guardar resultados de agentes
        for agent_name, agent_response in agent_responses.items():
            # Manejar tanto objetos AgentResponse como diccionarios
            if hasattr(agent_response, 'agent_name'):
                # Es un objeto AgentResponse
                db_agent_result = AgentResult(
                    listing_id=db_listing.id,
                    agent_name=agent_response.agent_name,
                    status=agent_response.status,
                    confidence=agent_response.confidence,
                    processing_time=agent_response.processing_time,
                    agent_data=agent_response.data,
                    notes=agent_response.notes,
                    recommendations=agent_response.recommendations
                )
            else:
                # Es un diccionario
                db_agent_result = AgentResult(
                    listing_id=db_listing.id,
                    agent_name=agent_response.get("agent_name", agent_name),
                    status=agent_response.get("status", "completed"),
                    confidence=agent_response.get("confidence", 0.0),
                    processing_time=agent_response.get("processing_time", 0.0),
                    agent_data=agent_response.get("data", {}),
                    notes=agent_response.get("notes", []),
                    recommendations=agent_response.get("recommendations", [])
                )
            self.db.add(db_agent_result)
        
        # Crear primera versión
        await self._create_version(db_listing, "Versión inicial")
        
        await self.db.commit()
        await self.db.refresh(db_listing)
        
        return db_listing
    
    async def get_listing(self, listing_id: int) -> Optional[Listing]:
        """
        Obtiene un listing por ID con todos sus datos relacionados
        """
        query = (
            select(Listing)
            .options(
                selectinload(Listing.agent_results),
                selectinload(Listing.listing_versions)
            )
            .where(Listing.id == listing_id)
        )
        
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_listings(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Listing]:
        """
        Obtiene lista de listings con filtros opcionales
        """
        query = select(Listing).order_by(desc(Listing.created_at))
        
        if status:
            query = query.where(Listing.status == status)
        
        if category:
            query = query.where(Listing.category == category)
        
        if search:
            query = query.where(
                Listing.product_name.ilike(f"%{search}%") |
                Listing.title.ilike(f"%{search}%")
            )
        
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_listing(
        self, 
        listing_id: int, 
        updates: Dict[str, Any],
        change_reason: Optional[str] = None
    ) -> Optional[Listing]:
        """
        Actualiza un listing y crea una nueva versión
        """
        listing = await self.get_listing(listing_id)
        if not listing:
            return None
        
        # Guardar versión actual antes de actualizar
        await self._create_version(listing, change_reason or "Actualización manual")
        
        # Aplicar actualizaciones
        for field, value in updates.items():
            if hasattr(listing, field):
                setattr(listing, field, value)
        
        # Incrementar versión
        listing.version += 1
        listing.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(listing)
        
        return listing
    
    async def delete_listing(self, listing_id: int) -> bool:
        """
        Elimina un listing (soft delete - cambia status a archived)
        """
        listing = await self.get_listing(listing_id)
        if not listing:
            return False
        
        listing.status = "archived"
        await self.db.commit()
        
        return True
    
    async def publish_listing(self, listing_id: int) -> Optional[Listing]:
        """
        Marca un listing como publicado
        """
        return await self.update_listing(
            listing_id, 
            {"status": "published"},
            "Listing publicado"
        )
    
    async def get_total_listings(self) -> int:
        """
        Obtiene el total de listings activos
        """
        query = select(Listing).where(Listing.status != "archived")
        result = await self.db.execute(query)
        return len(result.scalars().all())
    
    async def get_recent_listings(self, days: int = 7) -> List[Listing]:
        """
        Obtiene listings recientes de los últimos N días
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = (
            select(Listing)
            .where(
                and_(
                    Listing.created_at >= cutoff_date,
                    Listing.status != "archived"
                )
            )
            .order_by(desc(Listing.created_at))
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_category_stats(self) -> Dict[str, int]:
        """
        Obtiene estadísticas por categoría
        """
        query = select(Listing).where(Listing.status != "archived")
        result = await self.db.execute(query)
        listings = result.scalars().all()
        
        category_counts = {}
        for listing in listings:
            category = listing.category
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return category_counts
    
    async def get_confidence_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de confidence scores
        """
        query = select(Listing).where(Listing.status != "archived")
        result = await self.db.execute(query)
        listings = result.scalars().all()
        
        if not listings:
            return {"average": 0, "distribution": {}}
        
        scores = [listing.confidence_score for listing in listings]
        average = sum(scores) / len(scores)
        
        # Distribuir en rangos
        distribution = {
            "0.0-0.2": len([s for s in scores if 0.0 <= s < 0.2]),
            "0.2-0.4": len([s for s in scores if 0.2 <= s < 0.4]),
            "0.4-0.6": len([s for s in scores if 0.4 <= s < 0.6]),
            "0.6-0.8": len([s for s in scores if 0.6 <= s < 0.8]),
            "0.8-1.0": len([s for s in scores if 0.8 <= s <= 1.0])
        }
        
        return {
            "average": round(average, 3),
            "distribution": distribution,
            "min": min(scores),
            "max": max(scores),
            "total": len(scores)
        }
    
    async def get_processing_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de procesamiento
        """
        query = select(Listing).where(Listing.status != "archived")
        result = await self.db.execute(query)
        listings = result.scalars().all()
        
        if not listings:
            return {"success_rate": 0, "average_time": 0}
        
        # Calcular tasa de éxito basada en confidence scores
        successful_listings = [l for l in listings if l.confidence_score >= 0.6]
        success_rate = len(successful_listings) / len(listings)
        
        # Tiempo promedio de procesamiento (estimado basado en agentes)
        total_processing_time = 0
        total_agents = 0
        
        for listing in listings:
            for agent_result in listing.agent_results:
                total_processing_time += agent_result.processing_time if hasattr(agent_result, 'processing_time') else 5.0
                total_agents += 1
        
        average_time = total_processing_time / total_agents if total_agents > 0 else 0
        
        return {
            "success_rate": round(success_rate, 3),
            "average_time": round(average_time, 2),
            "total_processed": len(listings),
            "successful_count": len(successful_listings)
        }
    
    async def search_listings(self, query: str, limit: int = 20) -> List[Listing]:
        """
        Búsqueda avanzada de listings
        """
        search_query = (
            select(Listing)
            .where(
                and_(
                    Listing.status != "archived",
                    (
                        Listing.product_name.ilike(f"%{query}%") |
                        Listing.title.ilike(f"%{query}%") |
                        Listing.description.ilike(f"%{query}%")
                    )
                )
            )
            .order_by(desc(Listing.confidence_score))
            .limit(limit)
        )
        
        result = await self.db.execute(search_query)
        return result.scalars().all()
    
    async def get_listings_by_category(self, category: str) -> List[Listing]:
        """
        Obtiene listings por categoría
        """
        query = (
            select(Listing)
            .where(
                and_(
                    Listing.category == category,
                    Listing.status != "archived"
                )
            )
            .order_by(desc(Listing.created_at))
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def duplicate_listing(self, listing_id: int, new_name: str) -> Optional[Listing]:
        """
        Duplica un listing existente con un nuevo nombre
        """
        original = await self.get_listing(listing_id)
        if not original:
            return None
        
        # Crear nuevo listing basado en el original
        duplicated = Listing(
            product_name=new_name,
            category=original.category,
            target_price=original.target_price,
            input_data=original.input_data,
            title=original.title.replace(original.product_name, new_name),
            bullet_points=original.bullet_points,
            description=original.description.replace(original.product_name, new_name),
            search_terms=original.search_terms,
            backend_keywords=original.backend_keywords,
            images_order=original.images_order,
            a_plus_content=original.a_plus_content,
            confidence_score=original.confidence_score,
            processing_notes=[f"Duplicado de listing #{original.id}"] + (original.processing_notes or []),
            recommendations=original.recommendations,
            status="draft",
            version=1
        )
        
        self.db.add(duplicated)
        await self.db.flush()
        
        # Duplicar resultados de agentes
        for agent_result in original.agent_results:
            duplicated_agent = AgentResult(
                listing_id=duplicated.id,
                agent_name=agent_result.agent_name,
                status=agent_result.status,
                confidence=agent_result.confidence,
                processing_time=agent_result.processing_time,
                agent_data=agent_result.agent_data,
                notes=agent_result.notes,
                recommendations=agent_result.recommendations
            )
            self.db.add(duplicated_agent)
        
        await self.db.commit()
        await self.db.refresh(duplicated)
        
        return duplicated
    
    async def _create_version(self, listing: Listing, change_reason: str) -> ListingVersion:
        """
        Crea una nueva versión del listing para historial
        """
        version = ListingVersion(
            listing_id=listing.id,
            version_number=listing.version,
            title=listing.title,
            bullet_points=listing.bullet_points,
            description=listing.description,
            confidence_score=listing.confidence_score,
            change_reason=change_reason
        )
        
        self.db.add(version)
        return version
    
    async def update_agent_result(
        self,
        listing_id: int,
        agent_name: str,
        agent_result: Any
    ) -> Optional[AgentResult]:
        """
        Actualiza o crea un resultado de agente para un listing específico
        """
        try:
            # Crear nuevo resultado (simplificado por ahora)
            # TODO: Implementar lógica completa de actualización
            new_result = AgentResult(
                listing_id=listing_id,
                agent_name=agent_name,
                status="success",
                confidence=0.8,
                processing_time=0.0,
                agent_data=agent_result.data if hasattr(agent_result, 'data') else {},
                notes=[],
                recommendations=[]
            )
            
            self.db.add(new_result)
            await self.db.commit()
            return new_result
                
        except Exception as e:
            await self.db.rollback()
            raise e
