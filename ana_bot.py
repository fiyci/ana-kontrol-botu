"""
╔══════════════════════════════════════════════════════════════╗
║           ANA KONTROL BOTU v2.0                             ║
║  ✅ Join Request  🤖 Oto Mesaj  😀 Emoji  📢 Çoklu Kanal   ║
║  🖼 Görsel/Video  ✏️ Mesaj Düzenle  ➕ Kanal Ekle/Çıkar    ║
╚══════════════════════════════════════════════════════════════╝
"""

import logging, random, json, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ChatJoinRequestHandler, ContextTypes, filters
)

# ─── AYARLAR ───────────────────────────────────────────────────
BOT_TOKEN = "8743351745:AAGgX51IjWqSxNC6HY8yLINyabZ_4Dfq_Ow"
ADMIN_ID  = 7938675583
CONFIG    = "config.json"
# ───────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT = {
    "kanallar": [],          # [{"id": -100xxx, "isim": "Kanalım"}]
    "join_aktif": True,
    "join_medya_tip": "yok", # yok | foto | video
    "join_medya_id": "",     # file_id
    "join_mesaj": "👋 Merhaba <b>{first_name}</b>!\n\nKanalımıza hoş geldin! 🎉",
    "join_butonlar": [],     # [["Buton", "url"]]
    "oto_aktif": False,
    "oto_aralik": 3600,
    "oto_mesajlar": [
        "📢 Kanalımıza hoş geldiniz!",
        "🔥 Yeni içerikler için takipte kalın!",
        "💎 Sorularınız için yöneticiyle iletişime geçin."
    ],
    "oto_medya_tip": "yok",
    "oto_medya_id": "",
    "emoji_aktif": True,
    "emoji_kurallar": {
        "merhaba": "👋", "teşekkür": "🙏", "tebrik": "🎉",
        "harika": "🔥", "evet": "✅", "hayır": "❌",
        "para": "💰", "haha": "😂", "süper": "⭐", "bravo": "👏"
    },
    "stats": {"join": 0, "oto": 0, "emoji": 0}
}

# ─── CONFIG ────────────────────────────────────────────────────
def cfg():
    if os.path.exists(CONFIG):
        try:
            with open(CONFIG, encoding="utf-8") as f:
                data = json.load(f)
                # Eksik alanları DEFAULT'tan tamamla
                for k, v in DEFAULT.items():
                    if k not in data:
                        data[k] = v
                return data
        except: pass
    save(DEFAULT.copy())
    return DEFAULT.copy()

def save(c):
    with open(CONFIG, "w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False, indent=2)

def is_admin(uid): return uid == ADMIN_ID

# ─── KLAVYELER ─────────────────────────────────────────────────
def ana_kb():
    c = cfg()
    j = "🟢" if c["join_aktif"] else "🔴"
    o = "🟢" if c["oto_aktif"] else "🔴"
    e = "🟢" if c["emoji_aktif"] else "🔴"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{j} Join Request Bot", callback_data="m_join"),
         InlineKeyboardButton(f"{o} Otomatik Mesaj", callback_data="m_oto")],
        [InlineKeyboardButton(f"{e} Emoji Bot", callback_data="m_emoji"),
         InlineKeyboardButton("📢 Kanallar", callback_data="m_kanal")],
        [InlineKeyboardButton("📊 İstatistik", callback_data="m_stat"),
         InlineKeyboardButton("❓ Yardım", callback_data="m_yardim")],
    ])

def geri_kb(cb): return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data=cb)]])

# ─── START ─────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Erişim yok.")
    c = cfg()
    await update.message.reply_text(
        f"⚡ <b>Ana Kontrol Paneli v2.0</b>\n\n"
        f"📢 Kanal sayısı: <b>{len(c['kanallar'])}</b>\n"
        f"✉️ Join Bot: {'🟢 Aktif' if c['join_aktif'] else '🔴 Pasif'}\n"
        f"🤖 Oto Mesaj: {'🟢 Aktif' if c['oto_aktif'] else '🔴 Pasif'}\n"
        f"😀 Emoji Bot: {'🟢 Aktif' if c['emoji_aktif'] else '🔴 Pasif'}",
        parse_mode="HTML", reply_markup=ana_kb()
    )

async def ana_goster(query):
    c = cfg()
    await query.edit_message_text(
        f"⚡ <b>Ana Kontrol Paneli v2.0</b>\n\n"
        f"📢 Kanal sayısı: <b>{len(c['kanallar'])}</b>\n"
        f"✉️ Join Bot: {'🟢 Aktif' if c['join_aktif'] else '🔴 Pasif'}\n"
        f"🤖 Oto Mesaj: {'🟢 Aktif' if c['oto_aktif'] else '🔴 Pasif'}\n"
        f"😀 Emoji Bot: {'🟢 Aktif' if c['emoji_aktif'] else '🔴 Pasif'}",
        parse_mode="HTML", reply_markup=ana_kb()
    )

# ─── KANAL YÖNETİMİ ────────────────────────────────────────────
def kanal_kb():
    c = cfg()
    rows = []
    for i, k in enumerate(c["kanallar"]):
        rows.append([InlineKeyboardButton(f"❌ {k['isim']}", callback_data=f"kanal_sil_{i}")])
    rows.append([InlineKeyboardButton("➕ Kanal Ekle", callback_data="kanal_ekle")])
    rows.append([InlineKeyboardButton("🔙 Ana Menü", callback_data="ana")])
    return InlineKeyboardMarkup(rows)

async def kanal_menu(query):
    c = cfg()
    if c["kanallar"]:
        liste = "\n".join([f"• {k['isim']} (<code>{k['id']}</code>)" for k in c["kanallar"]])
    else:
        liste = "Henüz kanal eklenmemiş."
    await query.edit_message_text(
        f"📢 <b>Kanal Yönetimi</b>\n\n{liste}\n\n"
        f"➕ Kanal eklemek için butona bas.\n"
        f"❌ Kaldırmak için kanal adına bas.",
        parse_mode="HTML", reply_markup=kanal_kb()
    )

# ─── JOIN MENÜ ─────────────────────────────────────────────────
def join_kb():
    c = cfg()
    medya = c.get("join_medya_tip", "yok")
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔴 Kapat" if c["join_aktif"] else "🟢 Aç", callback_data="join_toggle")],
        [InlineKeyboardButton("✏️ Mesajı Düzenle", callback_data="join_mesaj_duzenle"),
         InlineKeyboardButton("👁 Mesajı Gör", callback_data="join_mesaj_gor")],
        [InlineKeyboardButton("🖼 Fotoğraf Ekle" if medya != "foto" else "🖼 Fotoğrafı Değiştir", callback_data="join_foto_ekle"),
         InlineKeyboardButton("🎬 Video Ekle" if medya != "video" else "🎬 Videoyu Değiştir", callback_data="join_video_ekle")],
        [InlineKeyboardButton("🔘 Buton Ekle", callback_data="join_buton_ekle"),
         InlineKeyboardButton("📋 Butonları Gör", callback_data="join_buton_gor")],
        [InlineKeyboardButton("🗑 Medyayı Kaldır", callback_data="join_medya_kaldir") if medya != "yok" else InlineKeyboardButton("─", callback_data="bos")],
        [InlineKeyboardButton("🔙 Ana Menü", callback_data="ana")],
    ])

async def join_menu(query):
    c = cfg()
    medya = c.get("join_medya_tip", "yok")
    medya_txt = {"yok": "❌ Yok", "foto": "📸 Fotoğraf", "video": "🎬 Video"}.get(medya, "❌ Yok")
    await query.edit_message_text(
        f"✉️ <b>Join Request Bot</b>\n\n"
        f"Durum: {'🟢 Aktif' if c['join_aktif'] else '🔴 Pasif'}\n"
        f"🖼 Medya: {medya_txt}\n"
        f"🔘 Buton sayısı: {len(c.get('join_butonlar', []))}",
        parse_mode="HTML", reply_markup=join_kb()
    )

# ─── OTO MESAJ MENÜ ────────────────────────────────────────────
def oto_kb():
    c = cfg()
    medya = c.get("oto_medya_tip", "yok")
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔴 Kapat" if c["oto_aktif"] else "🟢 Aç", callback_data="oto_toggle")],
        [InlineKeyboardButton("➕ Mesaj Ekle", callback_data="oto_ekle"),
         InlineKeyboardButton("📋 Mesajları Gör", callback_data="oto_liste")],
        [InlineKeyboardButton("🖼 Görsel Ekle" if medya != "foto" else "🖼 Görseli Değiştir", callback_data="oto_foto_ekle"),
         InlineKeyboardButton("🎬 Video Ekle" if medya != "video" else "🎬 Videoyu Değiştir", callback_data="oto_video_ekle")],
        [InlineKeyboardButton("⏱ Aralık Ayarla", callback_data="oto_aralik"),
         InlineKeyboardButton("📤 Şimdi Gönder", callback_data="oto_simdi")],
        [InlineKeyboardButton("🗑 Medyayı Kaldır", callback_data="oto_medya_kaldir") if medya != "yok" else InlineKeyboardButton("─", callback_data="bos")],
        [InlineKeyboardButton("🔙 Ana Menü", callback_data="ana")],
    ])

async def oto_menu(query):
    c = cfg()
    medya = c.get("oto_medya_tip", "yok")
    medya_txt = {"yok": "❌ Yok", "foto": "📸 Fotoğraf", "video": "🎬 Video"}.get(medya, "❌ Yok")
    await query.edit_message_text(
        f"🤖 <b>Otomatik Mesaj Bot</b>\n\n"
        f"Durum: {'🟢 Aktif' if c['oto_aktif'] else '🔴 Pasif'}\n"
        f"⏱ Aralık: {c['oto_aralik']/3600:.1f} saat\n"
        f"📝 Mesaj sayısı: {len(c['oto_mesajlar'])}\n"
        f"🖼 Medya: {medya_txt}",
        parse_mode="HTML", reply_markup=oto_kb()
    )

# ─── EMOJİ MENÜ ────────────────────────────────────────────────
def emoji_kb():
    c = cfg()
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔴 Kapat" if c["emoji_aktif"] else "🟢 Aç", callback_data="emoji_toggle")],
        [InlineKeyboardButton("➕ Kural Ekle", callback_data="emoji_ekle"),
         InlineKeyboardButton("📋 Kuralları Gör", callback_data="emoji_liste")],
        [InlineKeyboardButton("🔙 Ana Menü", callback_data="ana")],
    ])

async def emoji_menu(query):
    c = cfg()
    await query.edit_message_text(
        f"😀 <b>Emoji Bot</b>\n\n"
        f"Durum: {'🟢 Aktif' if c['emoji_aktif'] else '🔴 Pasif'}\n"
        f"📋 Kural sayısı: {len(c['emoji_kurallar'])}",
        parse_mode="HTML", reply_markup=emoji_kb()
    )

# ─── CALLBACK HANDLER ──────────────────────────────────────────
async def cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if not is_admin(q.from_user.id): return
    d = q.data
    c = cfg()

    if d == "ana": await ana_goster(q)
    elif d == "bos": pass

    # KANAL
    elif d == "m_kanal": await kanal_menu(q)
    elif d == "kanal_ekle":
        await q.edit_message_text(
            "📢 <b>Kanal Ekle</b>\n\n"
            "Kanalın ID'sini ve ismini şu formatta yaz:\n\n"
            "<code>ID|İsim</code>\n\n"
            "Örnek: <code>-1001234567890|Kanalım</code>\n\n"
            "Kanal ID'si için @userinfobot'u kanala ekle.",
            parse_mode="HTML",
            reply_markup=geri_kb("m_kanal")
        )
        context.user_data["bekle"] = "kanal_ekle"
    elif d.startswith("kanal_sil_"):
        idx = int(d.split("_")[-1])
        if 0 <= idx < len(c["kanallar"]):
            silinen = c["kanallar"].pop(idx)
            save(c)
            await q.answer(f"✅ {silinen['isim']} kaldırıldı!", show_alert=True)
        await kanal_menu(q)

    # JOIN
    elif d == "m_join": await join_menu(q)
    elif d == "join_toggle":
        c["join_aktif"] = not c["join_aktif"]
        save(c)
        await join_menu(q)
    elif d == "join_mesaj_gor":
        await q.edit_message_text(
            f"📝 <b>Mevcut Karşılama Mesajı:</b>\n\n{c['join_mesaj']}",
            parse_mode="HTML", reply_markup=geri_kb("m_join")
        )
    elif d == "join_mesaj_duzenle":
        await q.edit_message_text(
            "✏️ Yeni karşılama mesajını yaz:\n\n"
            "<code>{first_name}</code> = kullanıcı adı\n"
            "<b>kalın</b> = &lt;b&gt;kalın&lt;/b&gt;\n\n"
            "İptal: /iptal",
            parse_mode="HTML", reply_markup=geri_kb("m_join")
        )
        context.user_data["bekle"] = "join_mesaj"
    elif d == "join_foto_ekle":
        await q.edit_message_text("📸 Fotoğrafı gönder (direkt fotoğraf olarak):\n\nİptal: /iptal",
            reply_markup=geri_kb("m_join"))
        context.user_data["bekle"] = "join_foto"
    elif d == "join_video_ekle":
        await q.edit_message_text("🎬 Videoyu gönder (direkt video olarak):\n\nİptal: /iptal",
            reply_markup=geri_kb("m_join"))
        context.user_data["bekle"] = "join_video"
    elif d == "join_medya_kaldir":
        c["join_medya_tip"] = "yok"
        c["join_medya_id"] = ""
        save(c)
        await q.answer("✅ Medya kaldırıldı!", show_alert=True)
        await join_menu(q)
    elif d == "join_buton_ekle":
        await q.edit_message_text(
            "🔘 Buton ekle — şu formatta yaz:\n\n"
            "<code>Buton Adı|https://link.com</code>\n\n"
            "Örnek: <code>📢 Kanalımız|https://t.me/kanaladı</code>\n\nİptal: /iptal",
            parse_mode="HTML", reply_markup=geri_kb("m_join")
        )
        context.user_data["bekle"] = "join_buton"
    elif d == "join_buton_gor":
        butonlar = c.get("join_butonlar", [])
        if butonlar:
            liste = "\n".join([f"{i+1}. {b[0]} → {b[1]}" for i, b in enumerate(butonlar)])
            txt = f"🔘 <b>Butonlar:</b>\n\n{liste}\n\nSilmek için: /butonsil [numara]"
        else:
            txt = "Hiç buton eklenmemiş."
        await q.edit_message_text(txt, parse_mode="HTML", reply_markup=geri_kb("m_join"))

    # OTO MESAJ
    elif d == "m_oto": await oto_menu(q)
    elif d == "oto_toggle":
        c["oto_aktif"] = not c["oto_aktif"]
        save(c)
        await oto_menu(q)
    elif d == "oto_ekle":
        await q.edit_message_text("➕ Eklenecek mesajı yaz:\n\nİptal: /iptal", reply_markup=geri_kb("m_oto"))
        context.user_data["bekle"] = "oto_mesaj"
    elif d == "oto_liste":
        if c["oto_mesajlar"]:
            liste = "\n\n".join([f"<b>{i+1}.</b> {m}" for i, m in enumerate(c["oto_mesajlar"])])
            txt = f"📋 <b>Otomatik Mesajlar:</b>\n\n{liste}\n\nSilmek için: /otosil [numara]"
        else:
            txt = "Hiç mesaj yok. Eklemek için ➕ Mesaj Ekle."
        await q.edit_message_text(txt, parse_mode="HTML", reply_markup=geri_kb("m_oto"))
    elif d == "oto_foto_ekle":
        await q.edit_message_text("📸 Fotoğrafı gönder:\n\nİptal: /iptal", reply_markup=geri_kb("m_oto"))
        context.user_data["bekle"] = "oto_foto"
    elif d == "oto_video_ekle":
        await q.edit_message_text("🎬 Videoyu gönder:\n\nİptal: /iptal", reply_markup=geri_kb("m_oto"))
        context.user_data["bekle"] = "oto_video"
    elif d == "oto_medya_kaldir":
        c["oto_medya_tip"] = "yok"
        c["oto_medya_id"] = ""
        save(c)
        await q.answer("✅ Medya kaldırıldı!", show_alert=True)
        await oto_menu(q)
    elif d == "oto_aralik":
        await q.edit_message_text(
            "⏱ Aralığı <b>saat</b> olarak yaz:\n\n"
            "Örnekler: <code>1</code> | <code>2</code> | <code>6</code> | <code>12</code> | <code>24</code>\n\nİptal: /iptal",
            parse_mode="HTML", reply_markup=geri_kb("m_oto")
        )
        context.user_data["bekle"] = "oto_aralik"
    elif d == "oto_simdi":
        if not c["oto_mesajlar"]:
            await q.answer("❌ Hiç mesaj yok!", show_alert=True)
            return
        mesaj = random.choice(c["oto_mesajlar"])
        medya_tip = c.get("oto_medya_tip", "yok")
        medya_id = c.get("oto_medya_id", "")
        basarili = 0
        for kanal in c["kanallar"]:
            try:
                await _mesaj_gonder(context.bot, kanal["id"], mesaj, medya_tip, medya_id)
                basarili += 1
            except Exception as e:
                logger.error(f"Oto gönder hatası ({kanal['isim']}): {e}")
        c["stats"]["oto"] += basarili
        save(c)
        await q.answer(f"✅ {basarili} kanala gönderildi!", show_alert=True)

    # EMOJİ
    elif d == "m_emoji": await emoji_menu(q)
    elif d == "emoji_toggle":
        c["emoji_aktif"] = not c["emoji_aktif"]
        save(c)
        await emoji_menu(q)
    elif d == "emoji_ekle":
        await q.edit_message_text(
            "➕ Kural ekle:\n\n<code>kelime emoji</code>\n\nÖrnek: <code>merhaba 👋</code>\n\nİptal: /iptal",
            parse_mode="HTML", reply_markup=geri_kb("m_emoji")
        )
        context.user_data["bekle"] = "emoji_kural"
    elif d == "emoji_liste":
        if c["emoji_kurallar"]:
            liste = "\n".join([f"<b>{k}</b> → {v}" for k, v in c["emoji_kurallar"].items()])
            txt = f"📋 <b>Emoji Kuralları:</b>\n\n{liste}\n\nSilmek için: /emojisil [kelime]"
        else:
            txt = "Hiç kural yok."
        await q.edit_message_text(txt, parse_mode="HTML", reply_markup=geri_kb("m_emoji"))

    # İSTATİSTİK
    elif d == "m_stat":
        s = c["stats"]
        await q.edit_message_text(
            f"📊 <b>İstatistikler</b>\n\n"
            f"✉️ Join onaylanan: <b>{s['join']}</b>\n"
            f"🤖 Oto mesaj: <b>{s['oto']}</b>\n"
            f"😀 Emoji atılan: <b>{s['emoji']}</b>\n"
            f"📢 Kayıtlı kanal: <b>{len(c['kanallar'])}</b>",
            parse_mode="HTML", reply_markup=geri_kb("ana")
        )

    # YARDIM
    elif d == "m_yardim":
        await q.edit_message_text(
            "❓ <b>Yardım</b>\n\n"
            "/start — Ana menü\n"
            "/iptal — İşlemi iptal et\n"
            "/otosil [numara] — Oto mesaj sil\n"
            "/emojisil [kelime] — Emoji kuralı sil\n"
            "/butonsil [numara] — Join butonu sil\n\n"
            "<b>Kanal ID almak için:</b>\n"
            "@userinfobot'u kanala ekle → /start yaz",
            parse_mode="HTML", reply_markup=geri_kb("ana")
        )

# ─── MESAJ GÖNDERİCİ ───────────────────────────────────────────
async def _mesaj_gonder(bot, chat_id, metin, medya_tip, medya_id, butonlar=None):
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(b[0], url=b[1])] for b in butonlar]) if butonlar else None
    if medya_tip == "foto" and medya_id:
        await bot.send_photo(chat_id=chat_id, photo=medya_id, caption=metin, parse_mode="HTML", reply_markup=kb)
    elif medya_tip == "video" and medya_id:
        await bot.send_video(chat_id=chat_id, video=medya_id, caption=metin, parse_mode="HTML", reply_markup=kb)
    else:
        await bot.send_message(chat_id=chat_id, text=metin, parse_mode="HTML", reply_markup=kb)

# ─── MESAJ HANDLER ─────────────────────────────────────────────
async def mesaj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    bekle = context.user_data.get("bekle")
    c = cfg()

    # Fotoğraf geldi
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        if bekle == "join_foto":
            c["join_medya_tip"] = "foto"
            c["join_medya_id"] = file_id
            save(c)
            context.user_data["bekle"] = None
            await update.message.reply_text("✅ Join fotoğrafı kaydedildi!", reply_markup=ana_kb())
        elif bekle == "oto_foto":
            c["oto_medya_tip"] = "foto"
            c["oto_medya_id"] = file_id
            save(c)
            context.user_data["bekle"] = None
            await update.message.reply_text("✅ Oto mesaj fotoğrafı kaydedildi!", reply_markup=ana_kb())
        return

    # Video geldi
    if update.message.video:
        file_id = update.message.video.file_id
        if bekle == "join_video":
            c["join_medya_tip"] = "video"
            c["join_medya_id"] = file_id
            save(c)
            context.user_data["bekle"] = None
            await update.message.reply_text("✅ Join videosu kaydedildi!", reply_markup=ana_kb())
        elif bekle == "oto_video":
            c["oto_medya_tip"] = "video"
            c["oto_medya_id"] = file_id
            save(c)
            context.user_data["bekle"] = None
            await update.message.reply_text("✅ Oto mesaj videosu kaydedildi!", reply_markup=ana_kb())
        return

    metin = update.message.text
    if not metin: return

    # Emoji bot tetikleyici
    if not bekle and c["emoji_aktif"]:
        for kelime, emoji in c["emoji_kurallar"].items():
            if kelime.lower() in metin.lower():
                try:
                    await update.message.reply_text(emoji)
                    c["stats"]["emoji"] += 1
                    save(c)
                except: pass
                return

    if not bekle: return

    # Kanal ekle
    if bekle == "kanal_ekle":
        try:
            parcalar = metin.strip().split("|")
            kanal_id = int(parcalar[0].strip())
            isim = parcalar[1].strip() if len(parcalar) > 1 else str(kanal_id)
            c["kanallar"].append({"id": kanal_id, "isim": isim})
            save(c)
            context.user_data["bekle"] = None
            await update.message.reply_text(f"✅ Kanal eklendi: <b>{isim}</b>", parse_mode="HTML", reply_markup=ana_kb())
        except:
            await update.message.reply_text("❌ Format hatalı!\nDoğru format: <code>-1001234567890|Kanal Adı</code>", parse_mode="HTML")

    # Join mesaj
    elif bekle == "join_mesaj":
        c["join_mesaj"] = metin
        save(c)
        context.user_data["bekle"] = None
        await update.message.reply_text("✅ Karşılama mesajı güncellendi!", reply_markup=ana_kb())

    # Join buton
    elif bekle == "join_buton":
        try:
            parcalar = metin.strip().split("|")
            ad, url = parcalar[0].strip(), parcalar[1].strip()
            if "join_butonlar" not in c: c["join_butonlar"] = []
            c["join_butonlar"].append([ad, url])
            save(c)
            context.user_data["bekle"] = None
            await update.message.reply_text(f"✅ Buton eklendi: {ad}", reply_markup=ana_kb())
        except:
            await update.message.reply_text("❌ Format: <code>Buton Adı|https://link.com</code>", parse_mode="HTML")

    # Oto mesaj
    elif bekle == "oto_mesaj":
        c["oto_mesajlar"].append(metin)
        save(c)
        context.user_data["bekle"] = None
        await update.message.reply_text(f"✅ Mesaj eklendi!\n\n{metin}", reply_markup=ana_kb())

    # Oto aralik
    elif bekle == "oto_aralik":
        try:
            saat = float(metin.replace(",", "."))
            c["oto_aralik"] = int(saat * 3600)
            save(c)
            context.user_data["bekle"] = None
            await update.message.reply_text(f"✅ Aralık güncellendi: {saat} saat\n\n⚠️ Yeni aralık bir sonraki döngüde aktif olur.", reply_markup=ana_kb())
        except:
            await update.message.reply_text("❌ Sadece sayı gir. Örnek: 2")

    # Emoji kural
    elif bekle == "emoji_kural":
        parcalar = metin.strip().split()
        if len(parcalar) >= 2:
            kelime, emoji = parcalar[0].lower(), parcalar[1]
            c["emoji_kurallar"][kelime] = emoji
            save(c)
            context.user_data["bekle"] = None
            await update.message.reply_text(f"✅ Kural eklendi: <b>{kelime}</b> → {emoji}", parse_mode="HTML", reply_markup=ana_kb())
        else:
            await update.message.reply_text("❌ Format: <code>kelime 😀</code>", parse_mode="HTML")

# ─── KOMUTLAR ──────────────────────────────────────────────────
async def iptal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["bekle"] = None
    await update.message.reply_text("❌ İptal edildi.", reply_markup=ana_kb())

async def otosil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    c = cfg()
    if not context.args or not context.args[0].isdigit():
        return await update.message.reply_text("Kullanım: /otosil 2")
    idx = int(context.args[0]) - 1
    if 0 <= idx < len(c["oto_mesajlar"]):
        silinen = c["oto_mesajlar"].pop(idx)
        save(c)
        await update.message.reply_text(f"🗑 Silindi: {silinen}")
    else:
        await update.message.reply_text("❌ Geçersiz numara!")

async def emojisil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    c = cfg()
    if not context.args:
        return await update.message.reply_text("Kullanım: /emojisil kelime")
    kelime = context.args[0].lower()
    if kelime in c["emoji_kurallar"]:
        emoji = c["emoji_kurallar"].pop(kelime)
        save(c)
        await update.message.reply_text(f"🗑 Silindi: {kelime} → {emoji}")
    else:
        await update.message.reply_text(f"❌ '{kelime}' bulunamadı!")

async def butonsil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    c = cfg()
    if not context.args or not context.args[0].isdigit():
        return await update.message.reply_text("Kullanım: /butonsil 1")
    idx = int(context.args[0]) - 1
    butonlar = c.get("join_butonlar", [])
    if 0 <= idx < len(butonlar):
        silinen = butonlar.pop(idx)
        c["join_butonlar"] = butonlar
        save(c)
        await update.message.reply_text(f"🗑 Silindi: {silinen[0]}")
    else:
        await update.message.reply_text("❌ Geçersiz numara!")

# ─── JOIN REQUEST HANDLER ──────────────────────────────────────
async def join_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = cfg()
    if not c["join_aktif"]: return
    user = update.chat_join_request.from_user
    try:
        await _mesaj_gonder(
            context.bot, user.id,
            c["join_mesaj"].format(
                first_name=user.first_name or "Kullanıcı",
                last_name=user.last_name or "",
                username=user.username or ""
            ),
            c.get("join_medya_tip", "yok"),
            c.get("join_medya_id", ""),
            c.get("join_butonlar", [])
        )
        await update.chat_join_request.approve()
        c["stats"]["join"] += 1
        save(c)
        logger.info(f"✅ Join: {user.full_name}")
    except Exception as e:
        logger.error(f"Join hatası: {e}")
        try: await update.chat_join_request.approve()
        except: pass

# ─── OTO MESAJ JOB ─────────────────────────────────────────────
async def oto_job(context):
    c = cfg()
    if not c["oto_aktif"] or not c["oto_mesajlar"] or not c["kanallar"]: return
    mesaj = random.choice(c["oto_mesajlar"])
    for kanal in c["kanallar"]:
        try:
            await _mesaj_gonder(
                context.bot, kanal["id"], mesaj,
                c.get("oto_medya_tip", "yok"),
                c.get("oto_medya_id", "")
            )
            c["stats"]["oto"] += 1
            logger.info(f"✅ Oto → {kanal['isim']}")
        except Exception as e:
            logger.error(f"Oto hatası ({kanal['isim']}): {e}")
    save(c)

# ─── MAIN ──────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("iptal", iptal))
    app.add_handler(CommandHandler("otosil", otosil))
    app.add_handler(CommandHandler("emojisil", emojisil))
    app.add_handler(CommandHandler("butonsil", butonsil))
    app.add_handler(CallbackQueryHandler(cb))
    app.add_handler(ChatJoinRequestHandler(join_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, mesaj_handler))
    app.job_queue.run_repeating(oto_job, interval=3600, first=60)
    print("🚀 Ana Bot v2.0 başlatıldı!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
