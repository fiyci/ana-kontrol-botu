"""
╔══════════════════════════════════════════════════════════════╗
║           ANA KONTROL BOTU — Tek Bot, Tüm Özellikler        ║
║  ✅ Join Request Mesaj  🤖 Otomatik Mesaj  😀 Emoji Bot     ║
║  ✅ Toplu İstek Onay   📊 İstatistik      ⚙️ Ayarlar        ║
╚══════════════════════════════════════════════════════════════╝
"""

import logging
import random
import json
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ChatJoinRequestHandler,
    ContextTypes, ConversationHandler, filters
)

# ─── AYARLAR ───────────────────────────────────────────────────
BOT_TOKEN  = "8743351745:AAGgX51IjWqSxNC6HY8yLINyabZ_4Dfq_Ow"
ADMIN_ID   = 7938675583          # Kendi Telegram ID'n (@userinfobot ile öğren)
KANAL_ID   = -1003391807799
GRUP_ID    = 7938675583
CONFIG_DOSYA = "ana_config.json"
# ───────────────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Konuşma durumları
MESAJ_BEKLE, EMOJI_KELIME, EMOJI_EMOJI, ARALIK_BEKLE, KARSILAMA_BEKLE = range(5)

# ─── CONFIG ────────────────────────────────────────────────────
DEFAULT_CONFIG = {
    "join_aktif": True,
    "join_mesaj": "👋 Merhaba <b>{first_name}</b>!\n\nKanalımıza hoş geldin! 🎉\n\nHerhangi bir sorun için bizimle iletişime geç.",
    "join_butonlar": [["📢 Kanalımız", "https://t.me/+ntc34t0NtS9kYTg0"]],
    "oto_mesaj_aktif": False,
    "oto_mesaj_aralik": 3600,
    "oto_mesajlar": [
        "📢 Kanalımıza hoş geldiniz!",
        "🔥 Yeni içerikler için takipte kalın!",
        "💎 Sorularınız için @yonetici ile iletişime geçin."
    ],
    "emoji_aktif": True,
    "emoji_kurallar": {
        "merhaba": "👋", "teşekkür": "🙏", "tebrik": "🎉",
        "harika": "🔥", "evet": "✅", "hayır": "❌",
        "para": "💰", "haha": "😂", "süper": "⭐", "bravo": "👏"
    },
    "istatistik": {
        "join_onaylanan": 0,
        "oto_gonderilen": 0,
        "emoji_atilan": 0
    }
}

def cfg_yukle():
    if os.path.exists(CONFIG_DOSYA):
        with open(CONFIG_DOSYA, encoding="utf-8") as f:
            return json.load(f)
    cfg_kaydet(DEFAULT_CONFIG)
    return DEFAULT_CONFIG.copy()

def cfg_kaydet(c):
    with open(CONFIG_DOSYA, "w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False, indent=2)

def admin_mi(user_id):
    return user_id == ADMIN_ID

# ─── ANA MENÜ ──────────────────────────────────────────────────
def ana_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✉️ Join Request Bot", callback_data="menu_join"),
         InlineKeyboardButton("🤖 Otomatik Mesaj", callback_data="menu_oto")],
        [InlineKeyboardButton("😀 Emoji Bot", callback_data="menu_emoji"),
         InlineKeyboardButton("✅ Toplu Onay", callback_data="menu_onay")],
        [InlineKeyboardButton("📊 İstatistik", callback_data="menu_istat"),
         InlineKeyboardButton("⚙️ Genel Ayarlar", callback_data="menu_ayar")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not admin_mi(update.effective_user.id):
        return await update.message.reply_text("❌ Bu bota erişim izniniz yok.")
    cfg = cfg_yukle()
    join_durum = "🟢 Aktif" if cfg["join_aktif"] else "🔴 Pasif"
    oto_durum  = "🟢 Aktif" if cfg["oto_mesaj_aktif"] else "🔴 Pasif"
    emoji_durum= "🟢 Aktif" if cfg["emoji_aktif"] else "🔴 Pasif"
    await update.message.reply_text(
        f"⚡ <b>Ana Kontrol Paneli</b>\n\n"
        f"✉️ Join Bot: {join_durum}\n"
        f"🤖 Oto Mesaj: {oto_durum}\n"
        f"😀 Emoji Bot: {emoji_durum}\n\n"
        f"Yönetmek istediğin modülü seç:",
        parse_mode="HTML",
        reply_markup=ana_menu_keyboard()
    )

async def ana_menu_goster(query, cfg=None):
    if cfg is None:
        cfg = cfg_yukle()
    join_durum  = "🟢" if cfg["join_aktif"] else "🔴"
    oto_durum   = "🟢" if cfg["oto_mesaj_aktif"] else "🔴"
    emoji_durum = "🟢" if cfg["emoji_aktif"] else "🔴"
    await query.edit_message_text(
        f"⚡ <b>Ana Kontrol Paneli</b>\n\n"
        f"✉️ Join Bot: {join_durum}\n"
        f"🤖 Oto Mesaj: {oto_durum}\n"
        f"😀 Emoji Bot: {emoji_durum}\n\n"
        f"Yönetmek istediğin modülü seç:",
        parse_mode="HTML",
        reply_markup=ana_menu_keyboard()
    )

# ─── JOIN REQUEST MENÜ ─────────────────────────────────────────
def join_keyboard(aktif):
    durum_btn = "🔴 Kapat" if aktif else "🟢 Aç"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(durum_btn, callback_data="join_toggle")],
        [InlineKeyboardButton("✏️ Mesajı Değiştir", callback_data="join_mesaj_degistir")],
        [InlineKeyboardButton("👁 Mevcut Mesajı Gör", callback_data="join_mesaj_gor")],
        [InlineKeyboardButton("🔙 Ana Menü", callback_data="ana_menu")],
    ])

async def join_menu(query):
    cfg = cfg_yukle()
    durum = "🟢 Aktif" if cfg["join_aktif"] else "🔴 Pasif"
    await query.edit_message_text(
        f"✉️ <b>Join Request Bot</b>\n\nDurum: {durum}\n\n"
        f"Kanala istek atan kullanıcılara otomatik özel mesaj gönderir ve isteği onaylar.",
        parse_mode="HTML",
        reply_markup=join_keyboard(cfg["join_aktif"])
    )

# ─── OTO MESAJ MENÜ ────────────────────────────────────────────
def oto_keyboard(aktif):
    durum_btn = "🔴 Kapat" if aktif else "🟢 Aç"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(durum_btn, callback_data="oto_toggle")],
        [InlineKeyboardButton("➕ Mesaj Ekle", callback_data="oto_ekle"),
         InlineKeyboardButton("📋 Mesajları Gör", callback_data="oto_liste")],
        [InlineKeyboardButton("⏱ Aralık Değiştir", callback_data="oto_aralik"),
         InlineKeyboardButton("📤 Şimdi Gönder", callback_data="oto_simdi")],
        [InlineKeyboardButton("🔙 Ana Menü", callback_data="ana_menu")],
    ])

async def oto_menu(query):
    cfg = cfg_yukle()
    durum = "🟢 Aktif" if cfg["oto_mesaj_aktif"] else "🔴 Pasif"
    aralik_saat = cfg["oto_mesaj_aralik"] / 3600
    await query.edit_message_text(
        f"🤖 <b>Otomatik Mesaj Bot</b>\n\n"
        f"Durum: {durum}\n"
        f"⏱ Aralık: {aralik_saat:.1f} saat\n"
        f"📝 Mesaj sayısı: {len(cfg['oto_mesajlar'])}",
        parse_mode="HTML",
        reply_markup=oto_keyboard(cfg["oto_mesaj_aktif"])
    )

# ─── EMOJİ MENÜ ────────────────────────────────────────────────
def emoji_keyboard(aktif):
    durum_btn = "🔴 Kapat" if aktif else "🟢 Aç"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(durum_btn, callback_data="emoji_toggle")],
        [InlineKeyboardButton("➕ Kural Ekle", callback_data="emoji_ekle"),
         InlineKeyboardButton("📋 Kuralları Gör", callback_data="emoji_liste")],
        [InlineKeyboardButton("🔙 Ana Menü", callback_data="ana_menu")],
    ])

async def emoji_menu(query):
    cfg = cfg_yukle()
    durum = "🟢 Aktif" if cfg["emoji_aktif"] else "🔴 Pasif"
    await query.edit_message_text(
        f"😀 <b>Emoji Bot</b>\n\n"
        f"Durum: {durum}\n"
        f"📋 Kural sayısı: {len(cfg['emoji_kurallar'])}\n\n"
        f"Mesajlardaki kelimelere otomatik emoji tepkisi verir.",
        parse_mode="HTML",
        reply_markup=emoji_keyboard(cfg["emoji_aktif"])
    )

# ─── CALLBACK HANDLER ──────────────────────────────────────────
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not admin_mi(query.from_user.id):
        return

    data = query.data
    cfg = cfg_yukle()

    # Ana menü
    if data == "ana_menu":
        await ana_menu_goster(query, cfg)

    # JOIN menü
    elif data == "menu_join":
        await join_menu(query)

    elif data == "join_toggle":
        cfg["join_aktif"] = not cfg["join_aktif"]
        cfg_kaydet(cfg)
        await join_menu(query)

    elif data == "join_mesaj_gor":
        await query.edit_message_text(
            f"📝 <b>Mevcut Karşılama Mesajı:</b>\n\n{cfg['join_mesaj']}",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data="menu_join")]])
        )

    elif data == "join_mesaj_degistir":
        await query.edit_message_text(
            "✏️ Yeni karşılama mesajını yaz:\n\n"
            "<code>{first_name}</code> = kullanıcı adı\n"
            "HTML format desteklenir (<b>kalın</b>, <i>italik</i>)\n\n"
            "İptal için /iptal",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ İptal", callback_data="menu_join")]])
        )
        context.user_data["bekle"] = "join_mesaj"

    # OTO MESAJ menü
    elif data == "menu_oto":
        await oto_menu(query)

    elif data == "oto_toggle":
        cfg["oto_mesaj_aktif"] = not cfg["oto_mesaj_aktif"]
        cfg_kaydet(cfg)
        await oto_menu(query)

    elif data == "oto_liste":
        if not cfg["oto_mesajlar"]:
            text = "📭 Hiç mesaj yok."
        else:
            text = "📋 <b>Otomatik Mesajlar:</b>\n\n"
            for i, m in enumerate(cfg["oto_mesajlar"], 1):
                text += f"<b>{i}.</b> {m}\n\n"
            text += "Silmek için: /otosil [numara]"
        await query.edit_message_text(text, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data="menu_oto")]]))

    elif data == "oto_ekle":
        await query.edit_message_text(
            "➕ Eklenecek mesajı yaz:\n\nİptal için /iptal",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ İptal", callback_data="menu_oto")]])
        )
        context.user_data["bekle"] = "oto_mesaj"

    elif data == "oto_aralik":
        await query.edit_message_text(
            "⏱ Yeni aralığı <b>saat</b> cinsinden yaz:\n\nÖrnek: <code>1</code> = 1 saat, <code>6</code> = 6 saat\n\nİptal için /iptal",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ İptal", callback_data="menu_oto")]])
        )
        context.user_data["bekle"] = "oto_aralik"

    elif data == "oto_simdi":
        if not cfg["oto_mesajlar"]:
            await query.edit_message_text("❌ Hiç mesaj yok!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data="menu_oto")]]))
            return
        mesaj = random.choice(cfg["oto_mesajlar"])
        basarili = 0
        for hedef in [KANAL_ID, GRUP_ID]:
            try:
                await context.bot.send_message(chat_id=hedef, text=mesaj, parse_mode="HTML")
                basarili += 1
            except Exception as e:
                logger.error(f"Oto gönder hatası: {e}")
        cfg["istatistik"]["oto_gonderilen"] += basarili
        cfg_kaydet(cfg)
        await query.edit_message_text(
            f"✅ {basarili} hedefe gönderildi!\n\n{mesaj}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data="menu_oto")]]))

    # EMOJİ menü
    elif data == "menu_emoji":
        await emoji_menu(query)

    elif data == "emoji_toggle":
        cfg["emoji_aktif"] = not cfg["emoji_aktif"]
        cfg_kaydet(cfg)
        await emoji_menu(query)

    elif data == "emoji_liste":
        if not cfg["emoji_kurallar"]:
            text = "📭 Hiç kural yok."
        else:
            text = "📋 <b>Emoji Kuralları:</b>\n\n"
            for k, v in cfg["emoji_kurallar"].items():
                text += f"<b>{k}</b> → {v}\n"
            text += "\nSilmek için: /emojisil [kelime]"
        await query.edit_message_text(text, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data="menu_emoji")]]))

    elif data == "emoji_ekle":
        await query.edit_message_text(
            "➕ Kural ekle — şu formatta yaz:\n\n<code>kelime 😀</code>\n\nÖrnek: <code>merhaba 👋</code>\n\nİptal için /iptal",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ İptal", callback_data="menu_emoji")]])
        )
        context.user_data["bekle"] = "emoji_kural"

    # TOPLU ONAY
    elif data == "menu_onay":
        await query.edit_message_text(
            "✅ <b>Toplu İstek Onay</b>\n\n"
            "Bot otomatik olarak kanala gelen tüm üyelik isteklerini onaylıyor.\n\n"
            f"📊 Bugüne kadar onaylanan: <b>{cfg['istatistik']['join_onaylanan']}</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Ana Menü", callback_data="ana_menu")]]))

    # İSTATİSTİK
    elif data == "menu_istat":
        s = cfg["istatistik"]
        await query.edit_message_text(
            f"📊 <b>İstatistikler</b>\n\n"
            f"✉️ Join onaylanan : <b>{s['join_onaylanan']}</b>\n"
            f"🤖 Oto mesaj gönderilen: <b>{s['oto_gonderilen']}</b>\n"
            f"😀 Emoji atılan : <b>{s['emoji_atilan']}</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Ana Menü", callback_data="ana_menu")]]))

    # GENEL AYARLAR
    elif data == "menu_ayar":
        await query.edit_message_text(
            f"⚙️ <b>Genel Ayarlar</b>\n\n"
            f"🤖 Bot Token: <code>{'*' * 10 + BOT_TOKEN[-6:]}</code>\n"
            f"👤 Admin ID: <code>{ADMIN_ID}</code>\n"
            f"📢 Kanal ID: <code>{KANAL_ID}</code>\n"
            f"💬 Grup ID: <code>{GRUP_ID}</code>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Ana Menü", callback_data="ana_menu")]]))

# ─── MESAJ HANDLER (Beklenen girişler) ─────────────────────────
async def mesaj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not admin_mi(update.effective_user.id):
        return

    bekle = context.user_data.get("bekle")
    if not bekle:
        # Emoji bot aktifse normal mesajlara tepki ver
        cfg = cfg_yukle()
        if cfg["emoji_aktif"] and update.message.text:
            metin = update.message.text.lower()
            for kelime, emoji in cfg["emoji_kurallar"].items():
                if kelime.lower() in metin:
                    try:
                        await update.message.reply_text(emoji)
                        cfg["istatistik"]["emoji_atilan"] += 1
                        cfg_kaydet(cfg)
                    except: pass
                    return
        return

    metin = update.message.text
    cfg = cfg_yukle()

    if bekle == "join_mesaj":
        cfg["join_mesaj"] = metin
        cfg_kaydet(cfg)
        context.user_data["bekle"] = None
        await update.message.reply_text("✅ Karşılama mesajı güncellendi!", reply_markup=ana_menu_keyboard())

    elif bekle == "oto_mesaj":
        cfg["oto_mesajlar"].append(metin)
        cfg_kaydet(cfg)
        context.user_data["bekle"] = None
        await update.message.reply_text(f"✅ Mesaj eklendi!\n\n{metin}", reply_markup=ana_menu_keyboard())

    elif bekle == "oto_aralik":
        try:
            saat = float(metin.replace(",", "."))
            cfg["oto_mesaj_aralik"] = int(saat * 3600)
            cfg_kaydet(cfg)
            context.user_data["bekle"] = None
            await update.message.reply_text(f"✅ Aralık güncellendi: {saat} saat", reply_markup=ana_menu_keyboard())
        except:
            await update.message.reply_text("❌ Geçersiz! Sadece sayı gir. Örnek: 2")

    elif bekle == "emoji_kural":
        parcalar = metin.strip().split()
        if len(parcalar) >= 2:
            kelime, emoji = parcalar[0].lower(), parcalar[1]
            cfg["emoji_kurallar"][kelime] = emoji
            cfg_kaydet(cfg)
            context.user_data["bekle"] = None
            await update.message.reply_text(f"✅ Kural eklendi: <b>{kelime}</b> → {emoji}", parse_mode="HTML", reply_markup=ana_menu_keyboard())
        else:
            await update.message.reply_text("❌ Format: kelime 😀\nÖrnek: merhaba 👋")

# ─── KOMUTLAR ──────────────────────────────────────────────────
async def iptal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["bekle"] = None
    await update.message.reply_text("❌ İptal edildi.", reply_markup=ana_menu_keyboard())

async def otosil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not admin_mi(update.effective_user.id): return
    if not context.args or not context.args[0].isdigit():
        return await update.message.reply_text("Kullanım: /otosil 2")
    cfg = cfg_yukle()
    idx = int(context.args[0]) - 1
    if 0 <= idx < len(cfg["oto_mesajlar"]):
        silinen = cfg["oto_mesajlar"].pop(idx)
        cfg_kaydet(cfg)
        await update.message.reply_text(f"🗑 Silindi: {silinen}")
    else:
        await update.message.reply_text("❌ Geçersiz numara!")

async def emojisil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not admin_mi(update.effective_user.id): return
    if not context.args:
        return await update.message.reply_text("Kullanım: /emojisil kelime")
    cfg = cfg_yukle()
    kelime = context.args[0].lower()
    if kelime in cfg["emoji_kurallar"]:
        emoji = cfg["emoji_kurallar"].pop(kelime)
        cfg_kaydet(cfg)
        await update.message.reply_text(f"🗑 Silindi: {kelime} → {emoji}")
    else:
        await update.message.reply_text(f"❌ '{kelime}' bulunamadı!")

# ─── JOIN REQUEST HANDLER ──────────────────────────────────────
async def join_request_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cfg = cfg_yukle()
    if not cfg["join_aktif"]:
        return
    user = update.chat_join_request.from_user
    try:
        butonlar = [[InlineKeyboardButton(b[0], url=b[1])] for b in cfg.get("join_butonlar", [])]
        await context.bot.send_message(
            chat_id=user.id,
            text=cfg["join_mesaj"].format(
                first_name=user.first_name or "Kullanıcı",
                last_name=user.last_name or "",
                username=user.username or ""
            ),
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(butonlar) if butonlar else None
        )
        await update.chat_join_request.approve()
        cfg["istatistik"]["join_onaylanan"] += 1
        cfg_kaydet(cfg)
        logger.info(f"✅ Join onaylandı: {user.full_name}")
    except Exception as e:
        logger.error(f"Join hatası: {e}")
        await update.chat_join_request.approve()

# ─── OTO MESAJ JOB ─────────────────────────────────────────────
async def oto_mesaj_job(context):
    cfg = cfg_yukle()
    if not cfg["oto_mesaj_aktif"] or not cfg["oto_mesajlar"]:
        return
    mesaj = random.choice(cfg["oto_mesajlar"])
    for hedef in [KANAL_ID, GRUP_ID]:
        try:
            await context.bot.send_message(chat_id=hedef, text=mesaj, parse_mode="HTML")
            cfg["istatistik"]["oto_gonderilen"] += 1
            logger.info(f"✅ Oto mesaj gönderildi → {hedef}")
        except Exception as e:
            logger.error(f"Oto mesaj hatası ({hedef}): {e}")
    cfg_kaydet(cfg)

# ─── MAIN ──────────────────────────────────────────────────────
def main():
    if ADMIN_ID == 0:
        print("⚠️  ADMIN_ID girilmemiş! @userinfobot'tan ID'ni al ve ADMIN_ID'ye yaz.")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("iptal", iptal))
    app.add_handler(CommandHandler("otosil", otosil))
    app.add_handler(CommandHandler("emojisil", emojisil))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(ChatJoinRequestHandler(join_request_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_handler))

    # Otomatik mesaj job (her saat kontrol eder, config'e göre gönderir)
    app.job_queue.run_repeating(oto_mesaj_job, interval=3600, first=30)

    print("🚀 Ana Kontrol Botu başlatıldı!")
    print(f"📱 Telegram'dan /start komutunu gönder")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
