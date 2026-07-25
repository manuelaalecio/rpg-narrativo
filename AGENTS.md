# AGENTS.md

Este arquivo define as regras técnicas que **qualquer agente de IA** (opencode ou outro) deve seguir ao trabalhar neste projeto. As decisões aqui são derivadas de `docs/ADR-001-arquitetura.md` — em caso de dúvida, a ADR é a fonte da verdade; este arquivo é o resumo acionável dela.

Projeto: **RPG Narrativo em Python** (jogo de texto com interface gráfica própria, não roda em terminal).

---

## 1. Stack Técnica (não alterar sem atualizar a ADR)

- **Linguagem:** Python 3.11+
- **UI:** PySide6 (Qt for Python). **Nunca** usar Tkinter, PyQt6, Kivy ou DearPyGui neste projeto.
- **Persistência de conteúdo do jogo:** JSON em `data/`.
- **Persistência de save:** JSON via `infrastructure/persistence/`, acessado apenas através de um `Port` (interface) definido em `application/ports/`.
- **Testes:** `pytest`.
- **Gerenciador de dependências/ambiente:** `venv` + `pyproject.toml` (não introduzir Poetry/Conda sem justificativa).

---

## 2. Regra de Dependência entre Camadas (INVIOLÁVEL)

```
ui/            → pode importar presentation/
presentation/  → pode importar application/
application/   → pode importar domain/
domain/        → NÃO importa NADA de fora (nem application, nem infrastructure, nem ui, nem Qt)
infrastructure/→ implementa interfaces (Ports) definidas em application/ports/
```

**Nunca:**
- `domain/` importando `PySide6`, `json`, `sqlite3`, ou qualquer coisa de `ui/`/`infrastructure/`.
- `ui/` (Views) chamando `domain/` ou `application/` diretamente — sempre passar por `presentation/viewmodels/`.
- Lógica de negócio dentro de arquivos em `ui/`. Views só desenham e emitem sinais.

Se uma tarefa parecer exigir violar essa regra, pare e proponha um `Port`/`UseCase` novo em vez de importar direto.

---

## 3. Estrutura de Pastas (referência)

```
project/
├── main.py                # monta DI manual (liga Ports a implementações) e sobe a MainWindow
├── assets/                 # imagens, fontes, sons
├── data/                    # conteúdo do jogo em JSON: rooms/ items/ npcs/ dialogues/ quests/
├── domain/                  # entities/ value_objects/ events/ services/  (Python puro, sem I/O)
├── application/              # use_cases/  ports/ (repositories/, event_bus/)
├── infrastructure/            # persistence/ (json_repository.py, sqlite_repository.py futuro)
│                               # content_loader/  event_bus/ (in_memory_event_bus.py)
├── presentation/                # viewmodels/  state_machine/
├── ui/                            # windows/ screens/ widgets/  (PySide6, "burro")
├── services/                       # save_service.py, content_registry.py
├── save/                            # saves gerados em runtime (gitignored)
├── tests/                            # unit/ integration/ fixtures/
├── config/
└── docs/
    └── ADR-001-arquitetura-jogo-texto-python.md
```

Ao criar um arquivo novo, primeiro identifique em qual dessas pastas ele pertence com base na responsabilidade, não na conveniência.

---

## 4. Padrões de Projeto a Aplicar

| Situação | Padrão a usar |
|---|---|
| Criar `NPC`/`Item`/`Room` a partir de JSON | **Factory** em `infrastructure/content_loader/` |
| Regras de combate ou condições de diálogo com variações | **Strategy** |
| Reagir a algo que aconteceu no jogo (item pego, quest concluída) | **Observer** via Event Bus — nunca chamar o "interessado" diretamente |
| Ação do jogador (mover, atacar, usar item) | **Command**, disparado pela ViewModel e executado por um Use Case |
| Telas do jogo e nós de diálogo | **State** (State Machine explícita) |
| Acesso a save/conteúdo | **Repository**, sempre atrás de um `Port` |
| Ligar Use Cases a implementações concretas | **Dependency Injection manual** via construtor, montada em `main.py` — não usar framework de DI |
| Estado global | **Evitar Singleton.** Só usar se justificado explicitamente (ex: EventBus) e documentado no código |

---

## 5. Regras de Conteúdo (extensibilidade / OCP)

- Novo NPC, item, sala, quest ou diálogo = **novo arquivo JSON em `data/`**. Nunca editar código de domínio/aplicação para adicionar conteúdo.
- Condições em diálogos/quests (ex: "requer item X") devem ser **dados estruturados**, avaliados por um interpretador de condições no domínio. **Nunca usar `eval()`/`exec()`** ou scripts Python arbitrários para representar conteúdo.
- Ao adicionar um novo tipo de conteúdo, verificar primeiro se um `Factory`/`Registry` existente pode ser estendido antes de criar um novo mecanismo paralelo.

---

## 6. Convenções de Código

- Entidades de domínio: `@dataclass`, com type hints completos, sem métodos de I/O.
- Nomenclatura em **inglês** para código (classes, métodos, variáveis) — linguagem ubíqua do domínio: `Player`, `Room`, `Inventory`, `Quest`, `Dialogue`, `Combat`, `SaveGame`, `Event`.
- Docstrings em português ou inglês (manter consistência com o restante do arquivo em que se está editando).
- Eventos de domínio nomeados no passado: `ItemAdded`, `QuestCompleted`, `PlayerMoved`, `EnemyDefeated`.
- Um `UseCase` por ação relevante do jogador (ex: `MoveToRoomUseCase`, `StartDialogueUseCase`), com um método de entrada único e claro (`execute()`).
- ViewModels expõem apenas **estado observável primitivo** (strings, listas, bools, enums) para a View — nunca expõem entidades de domínio diretamente para `ui/`.

---

## 7. Testes

- Toda lógica em `domain/` e `application/` deve ter teste unitário em `tests/unit/`, sem instanciar Qt.
- Toda implementação em `infrastructure/` (ex: repositório JSON) deve ter teste de integração em `tests/integration/`.
- Ao criar um `Port` novo, criar também um Fake/Mock correspondente em `tests/fixtures/` para permitir testar `UseCases` sem depender da implementação real.
- Nenhuma tarefa é considerada concluída sem o teste correspondente, exceto ajustes puramente visuais em `ui/`.

---

## 8. O que NÃO fazer

- Não colocar lógica de negócio em handlers de sinais Qt (`ui/`).
- Não acoplar `domain/`/`application/` a PySide6, JSON, ou SQLite.
- Não introduzir banco de dados externo, servidor ou dependência de rede — o jogo é 100% local.
- Não usar `eval()`/`exec()` para interpretar conteúdo de diálogo/quest.
- Não adicionar frameworks de DI, ORM pesado, ou outras dependências não listadas na seção 1 sem antes propor a mudança e justificar (atualizando a ADR).
- Não migrar de JSON para SQLite antes de haver necessidade real (múltiplos slots de save, buscas) — YAGNI.

---

## 9. Ordem de Implementação (Roadmap)

Seguir esta ordem ao propor ou aceitar tarefas, salvo indicação contrária explícita do usuário:

1. Estrutura do projeto
2. Domínio (`Player`, `Room`, `Item`, `Map`)
3. Aplicação (use cases de exploração)
4. Infraestrutura mínima (leitura de JSON)
5. Interface gráfica base (janela principal + tela de exploração)
6. Navegação entre telas (State Machine)
7. Diálogos
8. Inventário
9. Save/Load
10. Quests
11. Combate
12. Event Bus integrando os módulos
13. Polimento
14. Testes abrangentes e documentação

---

## 10. Ao terminar uma tarefa

- Confirmar que nenhuma regra da seção 2 (dependência entre camadas) foi violada.
- Confirmar que testes relevantes foram adicionados/atualizados (seção 7).
- Se a tarefa exigir uma decisão arquitetural nova (ex: trocar padrão, adicionar dependência), propor uma atualização da ADR em vez de decidir silenciosamente.