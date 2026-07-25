from domain.entities.npc import NPC


class TestNPC:
    def test_create_npc(self) -> None:
        npc = NPC(id="npc_01", name="Guard", description="A town guard.")
        assert npc.id == "npc_01"
        assert npc.name == "Guard"
        assert npc.description == "A town guard."
        assert npc.dialogue_id is None

    def test_create_npc_with_dialogue(self) -> None:
        npc = NPC(id="npc_02", name="Merchant", description="A merchant.", dialogue_id="dlg_01")
        assert npc.dialogue_id == "dlg_01"
