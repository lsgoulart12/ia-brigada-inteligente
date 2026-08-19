from supabase import create_client, Client

# --- CONFIGURACAO SUPABASE ---
SUPABASE_URL = "https://seu-projeto-aqui.supabase.co"
SUPABASE_KEY = "sb_publishable_lI8HcYnr6pnQXdRUHrn1vQ_hldR_fIx"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def validar_tabela():
    try:
        dados = supabase.table("interacoes").select("*").limit(1).execute()
        print("Conexao OK. Tabela 'interacoes' encontrada.")
        print("Resposta Supabase:", dados)
    except Exception as db_err:
        erro = getattr(db_err, "message", None) or str(db_err)
        codigo = getattr(db_err, "code", None)
        detalhes = getattr(db_err, "details", None)
        dica = getattr(db_err, "hint", None)
        diagnostico = " | ".join(
            parte
            for parte in (
                f"codigo={codigo}" if codigo else "",
                erro,
                f"detalhes={detalhes}" if detalhes else "",
                f"dica={dica}" if dica else "",
            )
            if parte
        )
        print("Erro ao acessar tabela 'interacoes'")
        print("Diagnostico:", diagnostico)


if __name__ == "__main__":
    validar_tabela()
