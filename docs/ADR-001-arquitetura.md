# ADR-001: Arquitetura para Jogo de Texto (RPG Narrativo) em Python com Interface Gráfica

**Autor:** Arquitetura de Software
**Data:** 2026-07-25
**Status:** Proposta

---

## 1. Contexto

### Requisitos Funcionais

- O sistema deve exibir um jogo de texto (Text Adventure / RPG Narrativo) em uma **interface gráfica própria**, não em terminal.
- O jogador deve poder explorar cenários, interagir com NPCs, participar de diálogos ramificados, gerenciar inventário, cumprir missões (quests), participar de combates baseados em texto/turnos, salvar e carregar progresso, e alcançar múltiplos finais.
- O conteúdo (cenários, personagens, diálogos, itens, quests) deve poder ser expandido sem alterar o código-fonte do motor do jogo (extensibilidade de conteúdo, potencial suporte a mods).

### Requisitos Não Funcionais

- **Manutenibilidade:** o projeto crescerá ao longo do tempo; deve suportar novas features sem grandes refatorações.
- **Escalabilidade de conteúdo:** adicionar uma sala, item ou diálogo não deve exigir tocar em código de domínio ou de UI.
- **Testabilidade:** a lógica de jogo deve ser testável sem depender da interface gráfica.
- **Portabilidade:** deve rodar em Windows/Linux/macOS com Python puro e bibliotecas open source.
- **Desenvolvedor único, padrão profissional:** a arquitetura precisa ser simples o bastante para uma pessoa manter sozinha, mas organizada como se fosse um time trabalhando nela (separação clara de responsabilidades, documentação, testes).
- **Baixo custo de infraestrutura:** sem servidor, sem banco de dados externo — tudo local.
- **Performance aceitável para jogo de texto:** não há requisitos de tempo real; latência de UI deve ser imperceptível (<100ms por ação).

---

## 2. Objetivos Arquiteturais

| Objetivo | Como será perseguido |
|---|---|
| Modularidade | Separação em camadas (domínio, aplicação, infraestrutura, apresentação) e módulos por feature (diálogo, combate, inventário) |
| Baixo acoplamento | Domínio não conhece UI nem persistência; comunicação via interfaces (Protocols) e eventos |
| Alta coesão | Cada classe/módulo tem uma única responsabilidade clara (SRP) |
| Testabilidade | Regras de jogo isoladas em Python puro, sem dependência de framework gráfico |
| Escalabilidade | Novo conteúdo via dados (JSON) e registries/factories, não via edição de código existente (OCP) |
| Legibilidade | Nomenclatura de domínio (linguagem ubíqua/DDD), type hints, docstrings |
| Facilidade de adicionar conteúdo | Dados externos versionáveis, carregados dinamicamente |
| Separação lógica/interface | Domínio e Aplicação nunca importam código de UI; UI só chama a camada de Aplicação |

---

## 3. Tecnologias de Interface Gráfica

| Tecnologia | Vantagens | Desvantagens |
|---|---|---|
| **Tkinter** | Nativo do Python, zero dependências, leve, estável | Visual datado, poucos widgets ricos, layout manual trabalhoso para telas de texto/diálogo elaboradas |
| **CustomTkinter** | Visual moderno sobre Tkinter, curva de aprendizado baixa | Comunidade menor, menos maduro para apps grandes, ainda herda limitações do Tk em customização avançada |
| **PySide6 (Qt)** | Maduro, robusto, ótimo para apps desktop complexos, Qt Designer, licença LGPL (uso comercial livre), excelente suporte a temas, componentes ricos (QTextEdit, rich text, animações) | Peso maior de instalação (~150MB), curva de aprendizado mais alta, API extensa |
| **PyQt6** | Mesma engine Qt, muito documentado | Licença GPL/comercial paga para uso fechado — problema para um projeto que talvez queira flexibilidade de licenciamento futura |
| **DearPyGui** | Muito rápido (GPU-accelerated), ótimo para ferramentas/dashboards | Paradigma imediato (immediate mode) não é natural para apps orientados a estado como um RPG narrativo com telas persistentes; ecossistema menor |
| **Kivy** | Multiplataforma incluindo mobile, bom para jogos com gráficos | Voltado a touch/mobile e jogos com renderização própria; menos idiomático para uma UI de "aplicativo desktop" com texto rico, formulários e diálogos |

### Decisão: **PySide6**

Justificativa:
- Licença LGPL permite uso comercial e distribuição sem custos, ao contrário do PyQt6 (GPL/comercial).
- Suporta `QTextEdit`/`QTextBrowser` com HTML básico, ideal para exibir texto narrativo formatado (negrito, cores, quebras) sem reinventar renderização de texto.
- Sistema de **Signals & Slots** do Qt se integra naturalmente com um modelo MVVM/Observer, reduzindo acoplamento entre UI e lógica.
- Suporte a **QStackedWidget** para trocar de telas (menu, exploração, diálogo, combate, inventário) de forma limpa — mapeia bem para a State Machine de telas.
- Ecossistema maduro, muita documentação, Qt Designer para prototipar telas visualmente se desejado.
- Escala bem: o mesmo motor de UI atende de um protótipo simples a um jogo com muitas telas.

Trade-off aceito: tamanho de instalação maior e curva de aprendizado inicial mais alta que Tkinter — considerado aceitável pois o projeto pretende crescer e PySide6 evita reescrever a camada de UI mais adiante.

---

## 4. Arquitetura de Software

| Padrão | Resumo | Adequação ao projeto |
|---|---|---|
| **MVC** | Controller manipula Model e View diretamente | Simples, mas tende a Controllers "gordos" conforme features crescem (diálogo, combate, inventário todos no mesmo controller) |
| **MVP** | Presenter medeia toda comunicação, View é passiva | Bom desacoplamento, mas Presenter pode virar um ponto único inchado sem uma camada de aplicação por trás |
| **MVVM** | ViewModel expõe estado observável; View se liga via binding/eventos | Encaixa muito bem com Signals/Slots do Qt; ViewModel é testável sem instanciar widgets |
| **Clean Architecture** | Camadas concêntricas (Entities → Use Cases → Interface Adapters → Frameworks) com regra de dependência apontando para dentro | Ótima para isolar regras de negócio de frameworks (Qt, JSON, SQLite); pode ser "demais" se aplicada com todo o rigor formal para um único dev |
| **Hexagonal (Ports & Adapters)** | Domínio no centro, portas (interfaces) e adaptadores (implementações) nas bordas | Mesmo espírito da Clean Architecture; muito bom para trocar persistência (JSON→SQLite) ou UI sem tocar domínio |

### Decisão: **MVVM na camada de apresentação, combinado com princípios de Clean/Hexagonal nas camadas internas**

Isto é: o jogo terá **Domínio** (entidades e regras puras) → **Aplicação** (casos de uso/serviços, que são as "portas" no sentido hexagonal) → **Infraestrutura** (adaptadores: persistência em JSON, carregamento de conteúdo) → **Apresentação** (ViewModels + Views em Qt, seguindo MVVM).

Justificativa dos trade-offs:
- MVVM puro resolve bem a UI, mas sozinho não diz nada sobre como organizar regras de negócio — por isso ele governa apenas a camada de apresentação.
- Aplicar Clean Architecture/Hexagonal *com todo o cerimonial* (múltiplas interfaces para cada caso de uso, injeção de dependência formalizada em todos os pontos) seria over-engineering para um dev solo (viola YAGNI).
- A solução adotada pega o que interessa de cada abordagem: a **regra de dependência** (domínio não depende de nada externo) da Clean/Hexagonal, e o **binding reativo** do MVVM para a UI — sem exigir frameworks de DI complexos.

---

## 5. Organização do Projeto

```
project/
│
├── main.py                      # ponto de entrada; monta DI simples e inicia a janela principal
│
├── assets/                      # imagens, ícones, fontes, sons (se houver)
│   ├── images/
│   └── fonts/
│
├── data/                        # conteúdo do jogo em dados (não-código): salas, itens, diálogos, quests, npcs
│   ├── rooms/
│   ├── items/
│   ├── npcs/
│   ├── dialogues/
│   └── quests/
│
├── domain/                      # regras de negócio puras — SEM dependência de Qt, JSON, arquivos
│   ├── entities/                # Player, NPC, Item, Room, Quest, Dialogue, Combat, Map...
│   ├── value_objects/           # ex: Stats, Coordinates, ItemRarity
│   ├── events/                  # definições de eventos de domínio (QuestCompleted, ItemAdded...)
│   └── services/                # regras de domínio que não pertencem a uma única entidade (ex: CombatResolver)
│
├── application/                 # casos de uso / orquestração (a "porta" da arquitetura hexagonal)
│   ├── use_cases/                # ex: MoveToRoomUseCase, StartDialogueUseCase, SaveGameUseCase
│   └── ports/                    # interfaces (Protocols) que a infraestrutura deve implementar
│       ├── repositories/         # ex: SaveGameRepositoryPort, ContentRepositoryPort
│       └── event_bus/
│
├── infrastructure/               # implementações concretas dos ports
│   ├── persistence/
│   │   ├── json_repository.py
│   │   └── sqlite_repository.py  # (futuro)
│   ├── content_loader/            # lê data/ e converte em entidades de domínio
│   └── event_bus/
│       └── in_memory_event_bus.py
│
├── presentation/                  # ViewModels — estado observável para a UI, testável sem Qt
│   ├── viewmodels/
│   │   ├── exploration_viewmodel.py
│   │   ├── dialogue_viewmodel.py
│   │   ├── inventory_viewmodel.py
│   │   └── combat_viewmodel.py
│   └── state_machine/             # controla transições entre telas/estados do jogo
│
├── ui/                             # Views em PySide6 — apenas "burras", só desenham e emitem sinais
│   ├── windows/
│   │   └── main_window.py
│   ├── screens/
│   │   ├── main_menu_screen.py
│   │   ├── exploration_screen.py
│   │   ├── dialogue_screen.py
│   │   ├── inventory_screen.py
│   │   └── combat_screen.py
│   └── widgets/                    # componentes reutilizáveis (ex: painel de log de texto)
│
├── services/                       # serviços transversais de aplicação (não regra de negócio pura)
│   ├── save_service.py
│   └── content_registry.py         # registries/factories para NPCs, itens, eventos (extensibilidade OCP)
│
├── repositories/                   # (alternativa: pode ficar dentro de infrastructure/persistence)
│
├── save/                            # saves gerados pelo jogador em tempo de execução (gitignored)
│
├── tests/
│   ├── unit/                        # testes de domain/ e application/, sem Qt
│   ├── integration/                 # testes de infrastructure/ (ex: ler/escrever save)
│   └── fixtures/
│
└── config/                          # configurações (ex: caminhos, versão do save)
```

**Justificativa de cada pasta principal:**
- `domain/`: o coração do jogo. Não importa Qt, JSON nem SQLite. Pode ser testado com `pytest` puro.
- `application/`: orquestra o domínio para realizar casos de uso completos ("jogador entra na sala X", "jogador ataca o NPC Y"). Define **ports** (interfaces) que a infraestrutura implementa — isso é o que permite trocar JSON por SQLite sem tocar aqui.
- `infrastructure/`: tudo que é "detalhe técnico" — leitura de arquivo, banco de dados, serialização.
- `presentation/`: ViewModels que traduzem estado de domínio em algo que a View consome (strings, listas, flags), sem lógica de negócio.
- `ui/`: só desenha. Views delegam ações do usuário para ViewModels; nunca acessam `domain/` diretamente.
- `data/`: conteúdo do jogo como dados — permite adicionar uma nova sala/quest só criando um arquivo JSON, sem programar.
- `services/`: peças de suporte (save, registries) que não são regra pura de domínio, mas também não são infraestrutura bruta.
- `tests/`: espelha a separação de camadas, evidenciando que o domínio é testável isoladamente.

---

## 6. Modelagem de Entidades

| Entidade | Responsabilidade |
|---|---|
| `Player` | Estado do jogador: atributos, posição atual, inventário, quests ativas/concluídas |
| `NPC` | Personagem não jogável: identidade, diálogo associado, comportamento (hostil/pacífico) |
| `Item` | Definição de um item: nome, descrição, tipo, efeitos |
| `Inventory` | Coleção de itens de um `Player`; regras de adicionar/remover/limite de peso |
| `Quest` | Objetivo, estado (não iniciada/ativa/concluída/falhou), condições de conclusão |
| `Dialogue` | Árvore/grafo de falas e escolhas entre `Player` e `NPC` |
| `Event` | Representa algo que aconteceu no domínio (ex: `ItemAdded`), usado pelo barramento de eventos |
| `Room` | Um cenário: descrição, saídas, itens presentes, NPCs presentes |
| `Map` | Conjunto de `Room`s e suas conexões |
| `Combat` | Estado de um encontro de combate: participantes, turnos, regras de resolução |
| `SaveGame` | Snapshot serializável do estado necessário para retomar o jogo |

Cada entidade deve ser uma classe de domínio pura (idealmente `@dataclass`), sem métodos de I/O — apenas comportamento de negócio (ex: `Inventory.add_item()`, `Combat.resolve_turn()`).

---

## 7. Fluxo da Aplicação

```
Interface (ui/) — usuário clica em "Ir para o Norte"
        │  (sinal Qt)
        ▼
ViewModel (presentation/) — traduz a ação em uma chamada de caso de uso
        │
        ▼
Use Case (application/use_cases/) — ex: MoveToRoomUseCase
        │
        ▼
Domínio (domain/) — Room.get_exit("north"), regras de validação de movimento
        │
        ▼
Persistência (infrastructure/) — se necessário, salva estado via port de repositório
        │
        ▼
Evento de domínio disparado (ex: PlayerMoved) → event bus → outros sistemas reagem (ex: atualizar log)
        │
        ▼
ViewModel atualizado (estado observável muda)
        │  (sinal Qt)
        ▼
Interface re-renderiza a tela de exploração com a nova sala
```

A regra chave: **a seta nunca aponta de volta de dentro para fora** — `domain/` e `application/` nunca importam nada de `ui/` ou `infrastructure/`.

---

## 8. Persistência

| Opção | Vantagens | Desvantagens |
|---|---|---|
| **JSON** | Simples, humano-legível, zero dependência extra, fácil de versionar em Git (para conteúdo estático) | Sem transações, sem índices, arquivo inteiro precisa ser reescrito |
| **SQLite** | Transacional, consultas, bom para saves grandes/múltiplos slots, embutido no Python (`sqlite3`) | Overhead de schema/migrations para um projeto que começa pequeno |
| **YAML** | Muito legível para humanos editarem conteúdo (diálogos, quests) | Parsing mais lento, exige dependência externa (`pyyaml`), mais propenso a erros de indentação |

### Decisão

- **Conteúdo estático do jogo** (salas, itens, diálogos, quests): **JSON**, pois é nativo do Python (`json` builtin), fácil de versionar e de gerar/validar programaticamente.
- **Save do jogador**: começar com **JSON** por simplicidade (um save = um arquivo), e já isolar essa responsabilidade atrás de um `SaveGameRepositoryPort` em `application/ports/`.
- **Migração futura para SQLite**: como o acesso a dados já passa por uma interface (`Port`), basta criar `SQLiteSaveRepository` implementando o mesmo `Port` e trocar a injeção em `main.py` — sem alterar `domain/` nem `application/`. Faz sentido migrar quando houver necessidade de múltiplos slots de save com metadados pesquisáveis, ou New Game+/estatísticas históricas.

---

## 9. Engine de Diálogos

| Abordagem | Análise |
|---|---|
| JSON puro | Fácil de gerar/editar, mas fica verboso para lógica condicional (ex: "só mostra esta opção se item X estiver no inventário") |
| YAML | Mais legível que JSON para escrita manual, mesmas limitações de expressividade |
| Scripts Python | Máxima flexibilidade, mas acopla conteúdo a código — viola a meta de "adicionar diálogo sem tocar em código" e é arriscado (execução de código arbitrário se vier de mods) |
| Máquina de Estados | Boa para modelar diálogos como estados com transições, mas sozinha não organiza bem ramificações complexas com múltiplas falas |
| Árvore/Grafo de Diálogo | Modelo natural para diálogos com escolhas — cada nó é uma fala, cada aresta uma opção do jogador |

### Decisão: **Árvore/Grafo de Diálogo serializado em JSON, interpretado por uma pequena Máquina de Estados em domínio**

- O **dado** (o diálogo em si) fica em JSON, em `data/dialogues/`.
- O **domínio** interpreta esse grafo através de uma entidade `Dialogue` que se comporta como uma máquina de estados simples: nó atual → opções disponíveis (com condições avaliadas contra o estado do `Player`) → transição para o próximo nó.
- Condições (ex: "requer item X" ou "requer quest Y concluída") são representadas como dados estruturados (não código), avaliados por um pequeno interpretador de condições no domínio — isso evita `eval()`/scripts arbitrários e mantém segurança para suporte a mods no futuro.

---

## 10. Sistema de Eventos

Um **Event Bus** interno (Observer/Pub-Sub) desacopla os subsistemas: quem dispara um evento não precisa saber quem reage a ele.

Exemplos de eventos de domínio:
- `QuestCompleted(quest_id)`
- `ItemAdded(item_id, quantity)`
- `EnemyDefeated(enemy_id)`
- `PlayerMoved(from_room, to_room)`

Fluxo: um `UseCase` executa a ação de domínio → a entidade/serviço de domínio gera um `Event` → o `EventBus` (implementado em `infrastructure/event_bus/`, injetado via `Port`) notifica todos os `subscribers` registrados (ex: sistema de conquistas, log narrativo, atualização de ViewModel).

Isso permite, por exemplo, adicionar um sistema de conquistas no futuro **sem alterar** o código de combate ou de quests — basta assinar os eventos já existentes.

---

## 11. Gerenciamento de Estados (Telas)

Estados principais: `MainMenu`, `Loading`, `Exploration`, `Dialogue`, `Combat`, `Inventory`, `Paused`.

### Decisão: **State Machine explícita** em `presentation/state_machine/`, controlando qual tela (`QStackedWidget`) está ativa.

- Cada estado define quais transições são permitidas (ex: de `Exploration` pode-se ir para `Dialogue`, `Combat`, `Inventory` ou `Paused`; de `Combat` não se pode ir direto para `Dialogue`).
- Evita bugs de "telas impossíveis" (ex: abrir inventário durante a tela de carregamento) ao centralizar a validação de transições em um único lugar, em vez de espalhar `if`s pela UI.
- Mapeia diretamente para o padrão de projeto **State** (item 12).

---

## 12. Padrões de Projeto

| Padrão | Uso no projeto | Justificativa |
|---|---|---|
| **Factory** | Criar `NPC`, `Item`, `Room` a partir de dados JSON | Centraliza a lógica de "dado → objeto de domínio", facilitando adicionar novos tipos sem mudar quem consome |
| **Strategy** | Regras de resolução de combate, condições de diálogo | Permite trocar/expandir algoritmos (ex: tipo de dano) sem `if/elif` gigantes |
| **Observer** | Event Bus | Desacopla emissor de evento dos interessados nele |
| **Command** | Ações do jogador (mover, atacar, usar item) | Permite histórico de ações, possível undo/replay, e uniformiza como a UI dispara ações |
| **State** | Máquina de estados de telas e de diálogo | Encapsula comportamento e transições válidas por estado |
| **Repository** | Acesso a save games e a conteúdo | Isola domínio/aplicação da forma de armazenamento (JSON hoje, SQLite amanhã) |
| **Dependency Injection** (manual, via construtor) | Ligar `UseCases` aos `Repositories`/`EventBus` concretos em `main.py` | Mantém domínio testável com fakes/mocks, sem exigir um framework de DI pesado |
| **Singleton** | Apenas para o `EventBus` (opcionalmente) ou `ContentRegistry`, se justificado | Evitado por padrão pois dificulta testes; só usado se houver necessidade real de estado único global |

---

## 13. Escalabilidade (Open/Closed Principle)

- **Novos personagens/itens/quests/diálogos:** adicionados como novos arquivos JSON em `data/`, carregados dinamicamente pelo `content_loader`. Nenhum código existente precisa mudar.
- **Novos mapas:** um novo conjunto de `Room`s em `data/rooms/`, referenciado pelo `Map`.
- **Novas interfaces (ex: versão web futura):** como `ui/` só depende de `presentation/viewmodels/` (que por sua vez só depende de `application/`), uma nova camada de apresentação (ex: web) pode ser adicionada reaproveitando 100% de `domain/` e `application/`.
- **Novos tipos de evento/sistema (ex: conquistas):** basta assinar eventos já existentes no Event Bus.
- Extensão por **novos módulos/arquivos**, não por edição de módulos existentes, é o mecanismo central para cumprir o OCP aqui.

---

## 14. Testabilidade

- **Testes unitários** (`tests/unit/`): cobrem `domain/` e `application/` em isolamento, usando apenas `pytest` — sem instanciar Qt. Ex: testar `Inventory.add_item()` excede capacidade, testar `Dialogue` navega corretamente entre nós.
- **Testes de integração** (`tests/integration/`): validam `infrastructure/`, ex: salvar e recarregar um `SaveGame` via `JsonSaveRepository` e comparar igualdade.
- **Mocks/Fakes**: como `application/` depende de `Ports` (interfaces), é fácil criar `FakeSaveRepository` em memória para testar `UseCases` sem tocar disco.
- **Fixtures** (`tests/fixtures/`): dados de exemplo (JSON de sala, diálogo, item) reutilizados entre testes.
- ViewModels em `presentation/` também são testáveis sem UI real, pois expõem apenas estado (não widgets) — testa-se se o estado muda corretamente após uma ação.

---

## 15. Performance

Possíveis gargalos e mitigação:
- **Carregamento de conteúdo JSON grande de uma vez:** mitigar com carregamento lazy/sob demanda (carregar apenas a sala atual e adjacentes, não o mapa inteiro).
- **Re-renderização excessiva da UI:** usar sinais Qt granulares (emitir apenas quando o dado relevante muda), evitando redesenhar telas inteiras a cada ação pequena.
- **Escrita de save a cada ação:** salvar apenas em pontos definidos (auto-save periódico ou ao mudar de sala), não a cada clique.
- **Parsing repetido de diálogos/condições:** cachear o grafo de diálogo já parseado em memória enquanto a sessão estiver ativa.

Para um jogo de texto, esses gargalos são de baixo risco — o maior cuidado real é não bloquear a thread de UI com I/O (leitura de arquivo, save) demorado; usar `QThread`/sinais assíncronos do Qt se o save crescer muito.

---

## 16. Roadmap de Implementação

1. Estrutura do projeto e configuração inicial (pastas, `pyproject.toml`, ambiente virtual, dependências)
2. Camada de Domínio (entidades básicas: `Player`, `Room`, `Item`, `Map`)
3. Camada de Aplicação (use cases de exploração: mover, olhar, pegar item)
4. Infraestrutura mínima (leitura de JSON de `data/`)
5. Interface gráfica base (janela principal, `QStackedWidget`, tela de exploração)
6. Navegação entre telas (State Machine)
7. Sistema de diálogos (grafo + tela de diálogo)
8. Inventário (entidade + tela)
9. Sistema de Save/Load (JSON)
10. Sistema de Quests
11. Sistema de Combate
12. Sistema de eventos (Event Bus) integrando os módulos acima
13. Polimento (temas visuais, sons, ajustes de UX)
14. Testes abrangentes e documentação final

---

## 17. ADR Final

**Título:** Arquitetura em camadas (Domain/Application/Infrastructure/Presentation) com MVVM sobre PySide6 para RPG Narrativo em Python

**Status:** Proposta (aguardando validação antes da implementação)

**Contexto:**
Necessidade de construir um jogo de texto com interface gráfica própria em Python, com forte ênfase em extensibilidade de conteúdo e manutenibilidade a longo prazo, desenvolvido por um único desenvolvedor sob padrão profissional.

**Problema:**
Como estruturar o projeto para que novas funcionalidades (quests, combate, diálogos, mods) e conteúdo possam ser adicionadas continuamente, sem acoplar a lógica de jogo à tecnologia de UI ou de persistência, e mantendo tudo testável?

**Decisão:**
Adotar uma arquitetura em camadas — `domain` → `application` → `infrastructure`/`presentation` — com regra de dependência apontando para dentro (inspirada em Clean/Hexagonal Architecture), interface gráfica em **PySide6** organizada segundo **MVVM**, conteúdo de jogo em **JSON** carregado dinamicamente, comunicação entre subsistemas via **Event Bus** (Observer), e transições de tela controladas por **State Machine** explícita.

**Alternativas Consideradas:**
- Tkinter/CustomTkinter para UI: descartadas por limitações de componentes ricos para texto narrativo em telas mais complexas.
- PyQt6: descartado por questão de licenciamento (GPL) frente ao LGPL do PySide6.
- MVC/MVP puros: descartados por tenderem a Controllers/Presenters inchados conforme o projeto cresce.
- Clean Architecture/Hexagonal aplicadas com todo o formalismo: descartada a aplicação estrita por excesso de cerimônia para um dev solo; aproveitados os princípios centrais (regra de dependência, ports/adapters) sem o aparato completo.
- SQLite como persistência inicial: adiado para quando houver necessidade real (múltiplos slots, buscas), mantendo YAGNI.

**Consequências Positivas:**
- Domínio 100% testável sem depender de UI.
- Conteúdo novo adicionado via dados, sem recompilar/editar lógica.
- Troca futura de tecnologia de UI ou persistência isolada, sem reescrever regras de negócio.
- Arquitetura compreensível e documentada, facilitando retomar o projeto após pausas (comum em projetos solo).

**Consequências Negativas:**
- Mais arquivos e indireção (Ports, ViewModels, Use Cases) do que uma abordagem "tudo junto" — curva de entrada inicial maior.
- Exige disciplina do desenvolvedor único para não "furar" as camadas (ex: acessar domínio direto da `ui/` por atalho).

**Trade-offs:**
- Rigor arquitetural vs. velocidade inicial: opta-se por um pouco mais de esforço no início em troca de menor custo de manutenção depois.
- PySide6 vs. leveza do Tkinter: aceita-se maior peso de instalação em favor de melhores componentes de texto e melhor mapeamento para MVVM.

**Riscos:**
- Overengineering se as camadas forem aplicadas rigidamente demais para features pequenas — mitigado revisitando YAGNI a cada nova feature (nem tudo precisa de um Use Case dedicado).
- Desenvolvedor único pode divergir da arquitetura sob pressão de prazo — mitigado com testes automatizados que quebram se o domínio importar algo de `ui/`/`infrastructure/`.

**Próximos Passos:**
1. Validar esta ADR.
2. Executar os itens 1–4 do Roadmap (seção 16).
3. Revisar esta ADR após o primeiro marco funcional (exploração + diálogo básico) para confirmar se as decisões seguem válidas.
