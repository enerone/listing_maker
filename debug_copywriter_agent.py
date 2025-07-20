#!/usr/bin/env python3
"""
Debug script para verificar qué está generando el agente copywriter
"""

import asyncio
import sys
sys.path.append('/home/fabi/code/newlistings')

from app.agents.amazon_copywriter_agent import AmazonCopywriterAgent

async def debug_copywriter_agent():
    """Debug del agente copywriter"""
    
    print("🔍 DEBUG: Amazon Copywriter Agent")
    print("="*50)
    
    # Datos de prueba
    product_data = {
        "product_name": "Smartwatch Premium Serie X Pro",
        "value_proposition": "Reloj inteligente avanzado con monitoreo de salud, GPS, resistencia al agua y batería de larga duración",
        "category": "Electronics",
        "brand": "TechPro",
        "target_keywords": [
            "smartwatch", "reloj inteligente", "monitor cardiaco", "GPS", 
            "resistente agua", "fitness tracker", "batería larga", "premium"
        ],
        "competitive_advantages": [],
        "use_situations": [],
        "raw_specifications": "",
        "target_customer_description": "",
        "customer_analysis": {},
        "competitive_analysis": {},
        "seo_keywords": [
            "smartwatch", "reloj inteligente", "monitor cardiaco", "GPS", 
            "resistente agua", "fitness tracker", "batería larga", "premium"
        ]
    }
    
    try:
        # Instanciar y ejecutar agente
        copywriter_agent = AmazonCopywriterAgent()
        print(f"✅ Agente instanciado: {copywriter_agent.agent_name}")
        
        print("\n📤 Procesando datos del producto...")
        result = await copywriter_agent.process(product_data)
        
        print(f"📊 Status: {result.status}")
        print(f"📊 Confidence: {result.confidence}")
        
        if result.status == "success":
            print("\n🎯 DATOS GENERADOS:")
            print(f"Keys disponibles: {list(result.data.keys())}")
            
            # Verificar específicamente image_ai_prompts
            if "image_ai_prompts" in result.data:
                print("\n🎨 IMAGE AI PROMPTS ENCONTRADOS:")
                image_prompts = result.data["image_ai_prompts"]
                for prompt_type, prompt_text in image_prompts.items():
                    print(f"  {prompt_type}: {prompt_text}")
            else:
                print("\n❌ image_ai_prompts NO encontrado en result.data")
                
            # Mostrar una muestra de otros datos
            print("\n📝 OTROS DATOS GENERADOS:")
            for key, value in result.data.items():
                if key == "image_ai_prompts":
                    continue
                if isinstance(value, str):
                    print(f"  {key}: {value[:100]}{'...' if len(value) > 100 else ''}")
                elif isinstance(value, list):
                    print(f"  {key}: {len(value)} items")
                elif isinstance(value, dict):
                    print(f"  {key}: dict con {len(value)} keys")
                else:
                    print(f"  {key}: {type(value)}")
        else:
            print(f"❌ Error en agente: {result.notes}")
            
    except Exception as e:
        print(f"❌ Error ejecutando agente: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_copywriter_agent())
