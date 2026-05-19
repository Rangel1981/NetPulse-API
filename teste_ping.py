import subprocess
import httpx

# ⚠️ PREENCHA AQUI COM OS SEUS DADOS QUE VOCÊ PEGOU NO TELEGRAM
TELEGRAM_TOKEN = "8951336459:AAHgdnSt73bBO3PpxrUSChc-AkEuQtYWzs4"
CHAT_ID = "908602112"

def enviar_alerta_telegram(mensagem: str):
    """Função que faz uma requisição HTTP para a API do Telegram enviar uma mensagem"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem
    }
    
    try:
        # O httpx.post envia os dados para o Telegram através da internet
        resposta = httpx.post(url, json=payload)
        if resposta.status_code == 200:
            print("Alerta enviado para o Telegram com sucesso!")
        else:
            print(f"Falha ao enviar alerta. Status: {resposta.status_code}")
    except Exception as e:
        print(f"Erro de rede ao tentar falar com o Telegram: {e}")


def testar_ping(alvo: str) -> bool:
    print(f"Disparando ping para: {alvo}...")
    comando = ["ping", "-n", "1", "-w", "1000", alvo]
    resultado = subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return resultado.returncode == 0


# --- TESTANDO O FLUXO COMPLETO ---

# Vamos testar um IP que NÃO EXISTE para forçar uma falha e disparar o alerta
ip_teste = "1.2.3.4" 
status = testar_ping(ip_teste)

if status:
    print("O dispositivo está ONLINE. Nenhuma ação necessária.")
else:
    print("Aviso! O dispositivo está OFFLINE. 🚨")
    print("Disparando alerta...")
    
    mensagem_alerta = f"🚨 ATENÇÃO: O ativo {ip_teste} está OFFLINE! Verifique a infraestrutura imediatamente."
    enviar_alerta_telegram(mensagem_alerta)