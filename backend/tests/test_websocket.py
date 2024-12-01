import websockets
import asyncio
import json
import numpy as np
import time

async def test_websocket():
    uri = "ws://localhost:8000/api/v1/ws/stream"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Conectado ao servidor WebSocket")
            
            # Canais EEG
            channels = ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1',
                       'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4']
            
            # Simula envio de dados por 10 segundos
            for i in range(10):
                # Cria dados simulados
                data = {
                    "timestamp": time.time(),
                    "channels": {
                        ch: (np.sin(2 * np.pi * 10 * np.linspace(0, 1, 128)) + 
                             np.random.normal(0, 0.1, 128)).tolist()
                        for ch in channels
                    }
                }
                
                print(f"Enviando dados: {i+1}/10")
                
                # Envia dados
                try:
                    await websocket.send(json.dumps(data))
                    print("Dados enviados, aguardando resposta...")
                    
                    # Recebe resposta
                    response = await websocket.recv()
                    result = json.loads(response)
                    
                    # Mostra alguns resultados
                    if isinstance(result, dict) and "attention_metrics" in result:
                        print(f"Atenção: {result['attention_metrics']['attention_score']:.2f}")
                        print(f"Estado dos olhos: {result['attention_metrics']['eye_state']}")
                    else:
                        print("Resposta:", result)
                    print("---")
                    
                except Exception as e:
                    print(f"Erro ao enviar/receber dados: {str(e)}")
                    break
                
                # Aguarda um pouco
                await asyncio.sleep(1)
    
    except Exception as e:
        print(f"Erro na conexão WebSocket: {str(e)}")
        print(f"URI tentada: {uri}")

def main():
    print("Iniciando teste do WebSocket...")
    try:
        asyncio.run(test_websocket())
    except KeyboardInterrupt:
        print("\nTeste interrompido pelo usuário")
    except Exception as e:
        print(f"Erro ao executar teste: {str(e)}")

if __name__ == "__main__":
    main()