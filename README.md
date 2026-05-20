# ⚡ NetPulse - Monitoramento Assíncrono de Ativos de Rede

O **NetPulse** é um motor de monitoramento de infraestrutura de rede e gerência de ativos de alta performance construído com Python, FastAPI e SQLAlchemy. O sistema foi projetado sob o paradigma **assíncrono (não-bloqueante)** para permitir a varredura simultânea de múltiplos dispositivos de rede (via ICMP/Ping) sem causar engasgos ou travamentos nas rotas HTTP utilizadas pela interface de usuário.

## Diferenciais Técnicos & Arquitetura

Em sistemas tradicionais síncronos, o monitoramento de rede gera um gargalo de *I/O Bound* (espera ativa pelos pacotes). Se 50 dispositivos estiverem offline com um timeout de 3 segundos, a aplicação tradicional travaria por 150 segundos. 

O NetPulse soluciona esse problema através de:
- **Event Loop Distribuído:** Gerenciamento de subprocessos assíncronos do Sistema Operacional via `asyncio.create_subprocess_exec`.
- **Concorrência Consolida com `asyncio.gather`:** Disparo simultâneo de múltiplos testes ICMP na rede. O tempo de execução de cada ciclo passa a ser delimitado apenas pelo dispositivo de maior latência isolada, e não pela soma deles.
- **Isolamento de Estado (Sessões Limpas):** Varreduras executadas em segundo plano (*Background Tasks*) através dos ganchos de ciclo de vida (*Lifespan Events*) do FastAPI. A cada ciclo, uma sessão limpa e exclusiva do SQLAlchemy é criada e destruída, blindando o motor contra oscilações de rede no banco de dados.
- **Persistência em Lote (Bulk Commits):** Múltiplos registros de logs são consolidados na memória da sessão ORM e descarregados em uma única transação SQL, minimizando as viagens de rede (*Round-Trips*) com o banco.

---

##  Estrutura do Projeto

```text
app/
├── core/            # Configurações centrais (banco de dados, variáveis de ambiente)
├── models/          # Modelos ORM do SQLAlchemy (Asset, UptimeLog)
├── schemas/         # Esquemas de validação de dados com Pydantic
├── services/        # Lógica de negócio e motores assíncronos
│   └── monitor.py   # O Coração do Sistema (Captura ICMP & Orquestração do Ciclo)
└── main.py          # Ponto de entrada da API e gerenciamento do Lifespan