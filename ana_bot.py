"""
╔══════════════════════════════════════════════════════════════╗
║           ANA KONTROL BOTU v3.0                             ║
║  ✅ Join  🤖 Oto Mesaj  😀 Emoji  📢 Çoklu Kanal           ║
║  📊 Büyüme  💰 Ücretli Üyelik  📣 Çapraz  📰 RSS  🔐 Captcha ║
╚══════════════════════════════════════════════════════════════╝
"""

import logging, random, json, os, asyncio, feedparser
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
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
    "kanallar": [],
    "join_aktif": True,
    "join_medya_tip": "yok",
    "join_medya_id": "",
    "join_mesaj": "👋 Merhaba <b>{first_name}</b>!\n\nKanalımıza hoş geldin! 🎉",
    "join_butonlar": [],
    "oto_aktif": False,
    "oto_aralik": 3600,
    "oto_mesajlar": ["📢 Kanalımıza hoş geldiniz!", "🔥 Takipte kalın!"],
    "oto_medya_tip": "yok",
    "oto_medya_id": "",
    "emoji_aktif": True,
    "emoji_kurallar": {
        "merhaba": "👋", "teşekkür": "🙏", "tebrik": "🎉",
        "harika": "🔥", "evet": "✅", "hayır": "❌", "haha": "😂"
    },
    # Çapraz paylaşım
    "capraz_aktif": False,
    "capraz_kaynak": None,
    "capraz_hedefler": [],
    # RSS
    "rss_aktif": False,
    "rss_url": "",
    "rss_kanal": None,
    "rss_aralik": 3600,
    "rss_son_link": "",
    # Captcha
    "captcha_aktif": False,
    "captcha_sure": 120,
    "captcha_bekleyenler": {},
    # Ücretli üyelik
    "uyelik_aktif": False,
    "uyelik_fiyatlar": {
        "1ay":  {"fiyat": 50,  "label": "1 Aylık",   "gun": 30},
        "3ay":  {"fiyat": 120, "label": "3 Aylık",   "gun": 90},
        "yillik": {"fiyat": 400, "label": "Yıllık",  "gun": 365}
    },
    "uyelik_ton_adres": "BURAYA_TON_CUZDAN_ADRESINIZI_GIRIN",
    "uyelik_usdt_adres": "BURAYA_USDT_CUZDAN_ADRESINIZI_GIRIN",
    "uyelikler": {},
    # İstatistik
    "buyume": {},
    "stats": {"join": 0, "oto": 0, "emoji": 0, "uyelik_satis": 0}
}

def cfg():
    if os.path.exists(CONFIG):
        try:
            with open(CONFIG, encoding="utf-8") as f:
                data = json.load(f)
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

def bugun(): return datetime.now().strftime("%Y-%m-%d")

# ─── ANA MENÜ ──────────────────────────────────────────────────
def ana_kb():
    c = cfg()
    j = "🟢" if c["join_aktif"] else "🔴"
    o = "🟢" if c["oto_aktif"] else "🔴"
    e = "🟢" if c["emoji_aktif"] else "🔴"
    cap = "🟢" if c["captcha_aktif"] else "🔴"
    rss = "🟢" if c["rss_aktif"] else "🔴"
    uy  = "🟢" if c["uyelik_aktif"] else "🔴"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{j} Join Bot", callback_data="m_join"),
         InlineKeyboardButton(f"{o} Oto Mesaj", callback_data="m_oto")],
        [InlineKeyboardButton(f"{e} Emoji Bot", callback_data="m_emoji"),
         InlineKeyboardButton("📢 Kanallar", callback_data="m_kanal")],
        [InlineKeyboardButton(f"{cap} Captcha", callback_data="m_captcha"),
         InlineKeyboardButton(f"{rss} RSS Bot", callback_data="m_rss")],
        [InlineKeyboardButton("📣 Çapraz Paylaşım", callback_data="m_capraz"),
         InlineKeyboardButton(f"{uy} Ücretli Üyelik", callback_data="m_uyelik")],
        [InlineKeyboardButton("📊 Büyüme & İstatistik", callback_data="m_stat")],
    ])

def geri_kb(cb): return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data=cb)]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Erişim yok.")
    c = cfg()
    await update.message.reply_text(
        f"⚡ <b>Ana Kontrol Paneli v3.0</b>\n\n"
        f"📢 Kanal: <b>{len(c['kanallar'])}</b> adet\n"
        f"💰 Aktif üye: <b>{sum(1 for v in c['uyelikler'].values() if v.get('aktif'))}</b>\n"
        f"📊 Toplam join: <b>{c['stats']['join']}</b>",
        parse_mode="HTML", reply_markup=ana_kb()
    )

async def ana_goster(query):
    c = cfg()
    await query.edit_message_text(
        f"⚡ <b>Ana Kontrol Paneli v3.0</b>\n\n"
        f"📢 Kanal: <b>{len(c['kanallar'])}</b> adet\n"
        f"💰 Aktif üye: <b>{sum(1 for v in c['uyelikler'].values() if v.get('aktif'))}</b>\n"
        f"📊 Toplam join: <b>{c['stats']['join']}</b>",
        parse_mode="HTML", reply_markup=ana_kb()
    )

# ─── YARDIMCI ──────────────────────────────────────────────────
async def _mesaj_gonder(bot, chat_id, metin, medya_tip="yok", medya_id="", butonlar=None):
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(b[0], url=b[1])] for b in butonlar]) if butonlar else None
    if medya_tip == "foto" and medya_id:
        await bot.send_photo(chat_id=chat_id, photo=medya_id, caption=metin, parse_mode="HTML", reply_markup=kb)
    elif medya_tip == "video" and medya_id:
        await bot.send_video(chat_id=chat_id, video=medya_id, caption=metin, parse_mode="HTML", reply_markup=kb)
    else:
        await bot.send_message(chat_id=chat_id, text=metin, parse_mode="HTML", reply_markup=kb)

# ─── KANAL YÖNETİMİ ────────────────────────────────────────────
def kanal_kb():
    c = cfg()
    rows = [[InlineKeyboardButton(f"❌ {k['isim']}", callback_data=f"kanal_sil_{i}")] for i, k in enumerate(c["kanallar"])]
    rows.append([InlineKeyboardButton("➕ Kanal Ekle", callback_data="kanal_ekle")])
    rows.append([InlineKeyboardButton("🔙 Ana Menü", callback_data="ana")])
    return InlineKeyboardMarkup(rows)

async def kanal_menu(query):
    c = cfg()
    liste = "\n".join([f"• {k['isim']} (<code>{k['id']}</code>)" for k in c["kanallar"]]) or "Henüz kanal eklenmemiş."
    await query.edit_message_text(
        f"📢 <b>Kanal Yönetimi</b>\n\n{liste}\n\n"
        f"Format: <code>-1001234567890|Kanal Adı</code>",
        parse_mode="HTML", reply_markup=kanal_kb()
    )

# ─── JOIN MENÜ ─────────────────────────────────────────────────
async def join_menu(query):
    c = cfg()
    medya = {"yok": "❌", "foto": "📸", "video": "🎬"}.get(c.get("join_medya_tip", "yok"), "❌")
    await query.edit_message_text(
        f"✉️ <b>Join Request Bot</b>\n\n"
        f"Durum: {'🟢 Aktif' if c['join_aktif'] else '🔴 Pasif'}\n"
        f"Medya: {medya}  Buton: {len(c.get('join_butonlar', []))} adet",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔴 Kapat" if c["join_aktif"] else "🟢 Aç", callback_data="join_toggle")],
            [InlineKeyboardButton("✏️ Mesajı Düzenle", callback_data="join_mesaj_duzenle"),
             InlineKeyboardButton("👁 Mesajı Gör", callback_data="join_mesaj_gor")],
            [InlineKeyboardButton("🖼 Fotoğraf Ekle", callback_data="join_foto_ekle"),
             InlineKeyboardButton("🎬 Video Ekle", callback_data="join_video_ekle")],
            [InlineKeyboardButton("🔘 Buton Ekle", callback_data="join_buton_ekle"),
             InlineKeyboardButton("📋 Butonları Gör", callback_data="join_buton_gor")],
            [InlineKeyboardButton("🗑 Medyayı Kaldır", callback_data="join_medya_kaldir")],
            [InlineKeyboardButton("🔙 Ana Menü", callback_data="ana")],
        ])
    )

# ─── OTO MESAJ MENÜ ────────────────────────────────────────────
async def oto_menu(query):
    c = cfg()
    medya = {"yok": "❌", "foto": "📸", "video": "🎬"}.get(c.get("oto_medya_tip", "yok"), "❌")
    await query.edit_message_text(
        f"🤖 <b>Otomatik Mesaj</b>\n\n"
        f"Durum: {'🟢 Aktif' if c['oto_aktif'] else '🔴 Pasif'}\n"
        f"⏱ Aralık: {c['oto_aralik']/3600:.1f} saat\n"
        f"📝 Mesaj: {len(c['oto_mesajlar'])} adet  Medya: {medya}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔴 Kapat" if c["oto_aktif"] else "🟢 Aç", callback_data="oto_toggle")],
            [InlineKeyboardButton("➕ Mesaj Ekle", callback_data="oto_ekle"),
             InlineKeyboardButton("📋 Mesajları Gör", callback_data="oto_liste")],
            [InlineKeyboardButton("🖼 Fotoğraf Ekle", callback_data="oto_foto_ekle"),
             InlineKeyboardButton("🎬 Video Ekle", callback_data="oto_video_ekle")],
            [InlineKeyboardButton("⏱ Aralık Ayarla", callback_data="oto_aralik"),
             InlineKeyboardButton("📤 Şimdi Gönder", callback_data="oto_simdi")],
            [InlineKeyboardButton("🗑 Medyayı Kaldır", callback_data="oto_medya_kaldir")],
            [InlineKeyboardButton("🔙 Ana Menü", callback_data="ana")],
        ])
    )

# ─── EMOJİ MENÜ ────────────────────────────────────────────────
async def emoji_menu(query):
    c = cfg()
    await query.edit_message_text(
        f"😀 <b>Emoji Bot</b>\n\nDurum: {'🟢 Aktif' if c['emoji_aktif'] else '🔴 Pasif'}\n"
        f"Kural: {len(c['emoji_kurallar'])} adet",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔴 Kapat" if c["emoji_aktif"] else "🟢 Aç", callback_data="emoji_toggle")],
            [InlineKeyboardButton("➕ Kural Ekle", callback_data="emoji_ekle"),
             InlineKeyboardButton("📋 Kuralları Gör", callback_data="emoji_liste")],
            [InlineKeyboardButton("🔙 Ana Menü", callback_data="ana")],
        ])
    )

# ─── CAPTCHA MENÜ ──────────────────────────────────────────────
async def captcha_menu(query):
    c = cfg()
    await query.edit_message_text(
        f"🔐 <b>Captcha Sistemi</b>\n\n"
        f"Durum: {'🟢 Aktif' if c['captcha_aktif'] else '🔴 Pasif'}\n"
        f"⏱ Süre: {c['captcha_sure']} saniye\n"
        f"Tip: 🔢 Matematik sorusu\n\n"
        f"Yeni üye katıldığında matematik sorusu sorar, "
        f"doğru cevaplamazsa gruptan atar.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔴 Kapat" if c["captcha_aktif"] else "🟢 Aç", callback_data="captcha_toggle")],
            [InlineKeyboardButton("⏱ Süreyi Değiştir", callback_data="captcha_sure")],
            [InlineKeyboardButton("🔙 Ana Menü", callback_data="ana")],
        ])
    )

# ─── RSS MENÜ ──────────────────────────────────────────────────
async def rss_menu(query):
    c = cfg()
    kanal = next((k["isim"] for k in c["kanallar"] if k["id"] == c.get("rss_kanal")), "Seçilmedi")
    await query.edit_message_text(
        f"📰 <b>RSS Haber Botu</b>\n\n"
        f"Durum: {'🟢 Aktif' if c['rss_aktif'] else '🔴 Pasif'}\n"
        f"📡 RSS URL: {c.get('rss_url') or '—'}\n"
        f"📢 Hedef kanal: {kanal}\n"
        f"⏱ Kontrol aralığı: {c['rss_aralik']//60} dakika",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔴 Kapat" if c["rss_aktif"] else "🟢 Aç", callback_data="rss_toggle")],
            [InlineKeyboardButton("🔗 RSS URL Ayarla", callback_data="rss_url_ayarla"),
             InlineKeyboardButton("📢 Kanal Seç", callback_data="rss_kanal_sec")],
            [InlineKeyboardButton("⏱ Aralık Ayarla", callback_data="rss_aralik"),
             InlineKeyboardButton("🔄 Şimdi Kontrol Et", callback_data="rss_simdi")],
            [InlineKeyboardButton("🔙 Ana Menü", callback_data="ana")],
        ])
    )

# ─── ÇAPRAZ PAYLAŞIM MENÜ ──────────────────────────────────────
async def capraz_menu(query):
    c = cfg()
    kaynak = next((k["isim"] for k in c["kanallar"] if k["id"] == c.get("capraz_kaynak")), "Seçilmedi")
    hedef_isimleri = [k["isim"] for k in c["kanallar"] if k["id"] in c.get("capraz_hedefler", [])]
    await query.edit_message_text(
        f"📣 <b>Çapraz Paylaşım</b>\n\n"
        f"Durum: {'🟢 Aktif' if c['capraz_aktif'] else '🔴 Pasif'}\n"
        f"📥 Kaynak: {kaynak}\n"
        f"📤 Hedefler: {', '.join(hedef_isimleri) or '—'}\n\n"
        f"Kaynak kanaldan gelen her mesaj hedef kanallara iletilir.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔴 Kapat" if c["capraz_aktif"] else "🟢 Aç", callback_data="capraz_toggle")],
            [InlineKeyboardButton("📥 Kaynak Kanal Seç", callback_data="capraz_kaynak_sec"),
             InlineKeyboardButton("📤 Hedef Ekle/Çıkar", callback_data="capraz_hedef_sec")],
            [InlineKeyboardButton("🔙 Ana Menü", callback_data="ana")],
        ])
    )

# ─── ÜCRETLİ ÜYELİK MENÜ ──────────────────────────────────────
async def uyelik_menu(query):
    c = cfg()
    aktif_uye = sum(1 for v in c["uyelikler"].values() if v.get("aktif"))
    await query.edit_message_text(
        f"💰 <b>Ücretli Üyelik Sistemi</b>\n\n"
        f"Durum: {'🟢 Aktif' if c['uyelik_aktif'] else '🔴 Pasif'}\n"
        f"👥 Aktif üye: {aktif_uye}\n"
        f"💸 Toplam satış: {c['stats']['uyelik_satis']}\n\n"
        f"<b>Fiyatlar:</b>\n"
        + "\n".join([f"• {v['label']}: {v['fiyat']} USDT" for v in c['uyelik_fiyatlar'].values()]),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔴 Kapat" if c["uyelik_aktif"] else "🟢 Aç", callback_data="uyelik_toggle")],
            [InlineKeyboardButton("💲 Fiyat Ayarla", callback_data="uyelik_fiyat"),
             InlineKeyboardButton("👛 Cüzdan Ayarla", callback_data="uyelik_cuzdan")],
            [InlineKeyboardButton("👥 Üyeleri Gör", callback_data="uyelik_liste"),
             InlineKeyboardButton("✅ Ödeme Onayla", callback_data="uyelik_onayla")],
            [InlineKeyboardButton("🔙 Ana Menü", callback_data="ana")],
        ])
    )

# ─── İSTATİSTİK MENÜ ───────────────────────────────────────────
async def stat_menu(query):
    c = cfg()
    s = c["stats"]
    b = c.get("buyume", {})
    bugun_uye = b.get(bugun(), {}).get("katilan", 0)
    haftalik = sum(v.get("katilan", 0) for v in list(b.values())[-7:])
    await query.edit_message_text(
        f"📊 <b>Büyüme & İstatistik</b>\n\n"
        f"<b>Bugün:</b>\n"
        f"👥 Yeni üye: {bugun_uye}\n\n"
        f"<b>Son 7 gün:</b>\n"
        f"👥 Toplam katılan: {haftalik}\n\n"
        f"<b>Genel:</b>\n"
        f"✉️ Join onaylanan: {s['join']}\n"
        f"🤖 Oto mesaj: {s['oto']}\n"
        f"😀 Emoji: {s['emoji']}\n"
        f"💰 Üyelik satışı: {s['uyelik_satis']}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📈 Haftalık Rapor", callback_data="stat_haftalik")],
            [InlineKeyboardButton("🔙 Ana Menü", callback_data="ana")],
        ])
    )

# ─── CALLBACK HANDLER ──────────────────────────────────────────
async def cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if not is_admin(q.from_user.id): return
    d = q.data
    c = cfg()

    if d == "ana": await ana_goster(q)

    # KANAL
    elif d == "m_kanal": await kanal_menu(q)
    elif d == "kanal_ekle":
        await q.edit_message_text(
            "📢 <b>Kanal Ekle</b>\n\nFormat:\n<code>-1001234567890|Kanal Adı</code>\n\nİptal: /iptal",
            parse_mode="HTML", reply_markup=geri_kb("m_kanal"))
        context.user_data["bekle"] = "kanal_ekle"
    elif d.startswith("kanal_sil_"):
        idx = int(d.split("_")[-1])
        if 0 <= idx < len(c["kanallar"]):
            c["kanallar"].pop(idx)
            save(c)
        await kanal_menu(q)

    # JOIN
    elif d == "m_join": await join_menu(q)
    elif d == "join_toggle":
        c["join_aktif"] = not c["join_aktif"]; save(c); await join_menu(q)
    elif d == "join_mesaj_gor":
        await q.edit_message_text(f"📝 <b>Mesaj:</b>\n\n{c['join_mesaj']}", parse_mode="HTML", reply_markup=geri_kb("m_join"))
    elif d == "join_mesaj_duzenle":
        await q.edit_message_text("✏️ Yeni mesajı yaz:\n<code>{first_name}</code> = isim\n\nİptal: /iptal", parse_mode="HTML", reply_markup=geri_kb("m_join"))
        context.user_data["bekle"] = "join_mesaj"
    elif d == "join_foto_ekle":
        await q.edit_message_text("📸 Fotoğrafı gönder:\n\nİptal: /iptal", reply_markup=geri_kb("m_join"))
        context.user_data["bekle"] = "join_foto"
    elif d == "join_video_ekle":
        await q.edit_message_text("🎬 Videoyu gönder:\n\nİptal: /iptal", reply_markup=geri_kb("m_join"))
        context.user_data["bekle"] = "join_video"
    elif d == "join_medya_kaldir":
        c["join_medya_tip"] = "yok"; c["join_medya_id"] = ""; save(c)
        await q.answer("✅ Medya kaldırıldı!", show_alert=True); await join_menu(q)
    elif d == "join_buton_ekle":
        await q.edit_message_text("🔘 Format:\n<code>Buton Adı|https://link.com</code>\n\nİptal: /iptal", parse_mode="HTML", reply_markup=geri_kb("m_join"))
        context.user_data["bekle"] = "join_buton"
    elif d == "join_buton_gor":
        butonlar = c.get("join_butonlar", [])
        txt = "\n".join([f"{i+1}. {b[0]} → {b[1]}" for i, b in enumerate(butonlar)]) or "Hiç buton yok."
        await q.edit_message_text(f"🔘 <b>Butonlar:</b>\n\n{txt}\n\nSilmek: /butonsil [numara]", parse_mode="HTML", reply_markup=geri_kb("m_join"))

    # OTO MESAJ
    elif d == "m_oto": await oto_menu(q)
    elif d == "oto_toggle":
        c["oto_aktif"] = not c["oto_aktif"]; save(c); await oto_menu(q)
    elif d == "oto_ekle":
        await q.edit_message_text("➕ Mesajı yaz:\n\nİptal: /iptal", reply_markup=geri_kb("m_oto"))
        context.user_data["bekle"] = "oto_mesaj"
    elif d == "oto_liste":
        txt = "\n\n".join([f"<b>{i+1}.</b> {m}" for i, m in enumerate(c["oto_mesajlar"])]) or "Mesaj yok."
        await q.edit_message_text(f"📋 <b>Mesajlar:</b>\n\n{txt}\n\nSilmek: /otosil [numara]", parse_mode="HTML", reply_markup=geri_kb("m_oto"))
    elif d == "oto_foto_ekle":
        await q.edit_message_text("📸 Fotoğrafı gönder:\n\nİptal: /iptal", reply_markup=geri_kb("m_oto"))
        context.user_data["bekle"] = "oto_foto"
    elif d == "oto_video_ekle":
        await q.edit_message_text("🎬 Videoyu gönder:\n\nİptal: /iptal", reply_markup=geri_kb("m_oto"))
        context.user_data["bekle"] = "oto_video"
    elif d == "oto_medya_kaldir":
        c["oto_medya_tip"] = "yok"; c["oto_medya_id"] = ""; save(c)
        await q.answer("✅ Medya kaldırıldı!", show_alert=True); await oto_menu(q)
    elif d == "oto_aralik":
        await q.edit_message_text("⏱ Kaç saat? (örn: 2)\n\nİptal: /iptal", reply_markup=geri_kb("m_oto"))
        context.user_data["bekle"] = "oto_aralik"
    elif d == "oto_simdi":
        if not c["oto_mesajlar"] or not c["kanallar"]:
            await q.answer("❌ Mesaj veya kanal yok!", show_alert=True); return
        mesaj = random.choice(c["oto_mesajlar"])
        basarili = 0
        for k in c["kanallar"]:
            try:
                await _mesaj_gonder(context.bot, k["id"], mesaj, c.get("oto_medya_tip","yok"), c.get("oto_medya_id",""))
                basarili += 1
            except Exception as e: logger.error(f"Oto simdi: {e}")
        c["stats"]["oto"] += basarili; save(c)
        await q.answer(f"✅ {basarili} kanala gönderildi!", show_alert=True)

    # EMOJİ
    elif d == "m_emoji": await emoji_menu(q)
    elif d == "emoji_toggle":
        c["emoji_aktif"] = not c["emoji_aktif"]; save(c); await emoji_menu(q)
    elif d == "emoji_ekle":
        await q.edit_message_text("➕ Format:\n<code>kelime 😀</code>\n\nİptal: /iptal", parse_mode="HTML", reply_markup=geri_kb("m_emoji"))
        context.user_data["bekle"] = "emoji_kural"
    elif d == "emoji_liste":
        txt = "\n".join([f"<b>{k}</b> → {v}" for k, v in c["emoji_kurallar"].items()]) or "Kural yok."
        await q.edit_message_text(f"📋 <b>Kurallar:</b>\n\n{txt}\n\nSilmek: /emojisil [kelime]", parse_mode="HTML", reply_markup=geri_kb("m_emoji"))

    # CAPTCHA
    elif d == "m_captcha": await captcha_menu(q)
    elif d == "captcha_toggle":
        c["captcha_aktif"] = not c["captcha_aktif"]; save(c); await captcha_menu(q)
    elif d == "captcha_sure":
        await q.edit_message_text("⏱ Kaç saniye? (örn: 120)\n\nİptal: /iptal", reply_markup=geri_kb("m_captcha"))
        context.user_data["bekle"] = "captcha_sure"

    # RSS
    elif d == "m_rss": await rss_menu(q)
    elif d == "rss_toggle":
        c["rss_aktif"] = not c["rss_aktif"]; save(c); await rss_menu(q)
    elif d == "rss_url_ayarla":
        await q.edit_message_text("🔗 RSS feed URL'ini yaz:\n\nÖrnek: https://site.com/rss.xml\n\nİptal: /iptal", reply_markup=geri_kb("m_rss"))
        context.user_data["bekle"] = "rss_url"
    elif d == "rss_kanal_sec":
        if not c["kanallar"]:
            await q.answer("❌ Önce kanal ekle!", show_alert=True); return
        rows = [[InlineKeyboardButton(k["isim"], callback_data=f"rss_kanal_{i}")] for i, k in enumerate(c["kanallar"])]
        rows.append([InlineKeyboardButton("🔙 Geri", callback_data="m_rss")])
        await q.edit_message_text("📢 RSS için hedef kanalı seç:", reply_markup=InlineKeyboardMarkup(rows))
    elif d.startswith("rss_kanal_"):
        idx = int(d.split("_")[-1])
        c["rss_kanal"] = c["kanallar"][idx]["id"]; save(c)
        await q.answer(f"✅ {c['kanallar'][idx]['isim']} seçildi!", show_alert=True); await rss_menu(q)
    elif d == "rss_aralik":
        await q.edit_message_text("⏱ Kontrol aralığı (dakika):\n\nÖrnek: 30\n\nİptal: /iptal", reply_markup=geri_kb("m_rss"))
        context.user_data["bekle"] = "rss_aralik"
    elif d == "rss_simdi":
        await q.answer("🔄 Kontrol ediliyor...", show_alert=False)
        await rss_kontrol(context)
        await q.answer("✅ Kontrol tamamlandı!", show_alert=True)

    # ÇAPRAZ PAYLAŞIM
    elif d == "m_capraz": await capraz_menu(q)
    elif d == "capraz_toggle":
        c["capraz_aktif"] = not c["capraz_aktif"]; save(c); await capraz_menu(q)
    elif d == "capraz_kaynak_sec":
        if not c["kanallar"]:
            await q.answer("❌ Önce kanal ekle!", show_alert=True); return
        rows = [[InlineKeyboardButton(k["isim"], callback_data=f"capraz_k_{i}")] for i, k in enumerate(c["kanallar"])]
        rows.append([InlineKeyboardButton("🔙 Geri", callback_data="m_capraz")])
        await q.edit_message_text("📥 Kaynak kanalı seç:", reply_markup=InlineKeyboardMarkup(rows))
    elif d.startswith("capraz_k_"):
        idx = int(d.split("_")[-1])
        c["capraz_kaynak"] = c["kanallar"][idx]["id"]; save(c)
        await q.answer(f"✅ Kaynak: {c['kanallar'][idx]['isim']}", show_alert=True); await capraz_menu(q)
    elif d == "capraz_hedef_sec":
        if not c["kanallar"]:
            await q.answer("❌ Önce kanal ekle!", show_alert=True); return
        rows = []
        for i, k in enumerate(c["kanallar"]):
            if k["id"] == c.get("capraz_kaynak"): continue
            secili = "✅" if k["id"] in c.get("capraz_hedefler", []) else "◻️"
            rows.append([InlineKeyboardButton(f"{secili} {k['isim']}", callback_data=f"capraz_h_{i}")])
        rows.append([InlineKeyboardButton("🔙 Geri", callback_data="m_capraz")])
        await q.edit_message_text("📤 Hedef kanalları seç (birden fazla seçebilirsin):", reply_markup=InlineKeyboardMarkup(rows))
    elif d.startswith("capraz_h_"):
        idx = int(d.split("_")[-1])
        kid = c["kanallar"][idx]["id"]
        if "capraz_hedefler" not in c: c["capraz_hedefler"] = []
        if kid in c["capraz_hedefler"]: c["capraz_hedefler"].remove(kid)
        else: c["capraz_hedefler"].append(kid)
        save(c)
        rows = []
        for i, k in enumerate(c["kanallar"]):
            if k["id"] == c.get("capraz_kaynak"): continue
            secili = "✅" if k["id"] in c["capraz_hedefler"] else "◻️"
            rows.append([InlineKeyboardButton(f"{secili} {k['isim']}", callback_data=f"capraz_h_{i}")])
        rows.append([InlineKeyboardButton("🔙 Geri", callback_data="m_capraz")])
        await q.edit_message_text("📤 Hedef kanalları seç:", reply_markup=InlineKeyboardMarkup(rows))

    # ÜCRETLİ ÜYELİK
    elif d == "m_uyelik": await uyelik_menu(q)
    elif d == "uyelik_toggle":
        c["uyelik_aktif"] = not c["uyelik_aktif"]; save(c); await uyelik_menu(q)
    elif d == "uyelik_fiyat":
        await q.edit_message_text(
            "💲 Fiyat güncelle. Format:\n<code>1ay|50</code> veya <code>3ay|120</code> veya <code>yillik|400</code>\n\nİptal: /iptal",
            parse_mode="HTML", reply_markup=geri_kb("m_uyelik"))
        context.user_data["bekle"] = "uyelik_fiyat"
    elif d == "uyelik_cuzdan":
        await q.edit_message_text(
            "👛 Cüzdan adresini güncelle. Format:\n<code>ton|ADRES</code> veya <code>usdt|ADRES</code>\n\nİptal: /iptal",
            parse_mode="HTML", reply_markup=geri_kb("m_uyelik"))
        context.user_data["bekle"] = "uyelik_cuzdan"
    elif d == "uyelik_liste":
        uyelikler = [(uid, v) for uid, v in c["uyelikler"].items() if v.get("aktif")]
        if uyelikler:
            txt = "\n".join([f"👤 {v.get('isim','?')} — {v.get('plan','?')} — Bitiş: {v.get('bitis','?')}" for uid, v in uyelikler])
        else:
            txt = "Aktif üye yok."
        await q.edit_message_text(f"👥 <b>Aktif Üyeler:</b>\n\n{txt}", parse_mode="HTML", reply_markup=geri_kb("m_uyelik"))
    elif d == "uyelik_onayla":
        await q.edit_message_text(
            "✅ Ödemeyi onaylamak için:\n<code>/onayla [kullanici_id] [1ay|3ay|yillik]</code>\n\nÖrnek: /onayla 123456789 1ay",
            parse_mode="HTML", reply_markup=geri_kb("m_uyelik"))

    # İSTATİSTİK
    elif d == "m_stat": await stat_menu(q)
    elif d == "stat_haftalik":
        b = c.get("buyume", {})
        gunler = sorted(b.keys())[-7:]
        txt = "\n".join([f"📅 {g}: +{b[g].get('katilan',0)} üye" for g in gunler]) or "Veri yok."
        await q.edit_message_text(f"📈 <b>Son 7 Gün:</b>\n\n{txt}", parse_mode="HTML", reply_markup=geri_kb("m_stat"))

# ─── MESAJ HANDLER ─────────────────────────────────────────────
async def mesaj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    uid = update.effective_user.id
    c = cfg()

    # Captcha cevabı (admin olmayan)
    if not is_admin(uid) and str(uid) in c.get("captcha_bekleyenler", {}):
        bekleyen = c["captcha_bekleyenler"][str(uid)]
        if update.message.text and update.message.text.strip() == str(bekleyen["cevap"]):
            del c["captcha_bekleyenler"][str(uid)]
            save(c)
            await update.message.reply_text("✅ Doğrulandın! Hoş geldin 🎉")
        else:
            await update.message.reply_text("❌ Yanlış! Tekrar dene.")
        return

    if not is_admin(uid):
        # Emoji bot
        if c["emoji_aktif"] and update.message.text:
            for kelime, emoji in c["emoji_kurallar"].items():
                if kelime.lower() in update.message.text.lower():
                    try:
                        await update.message.reply_text(emoji)
                        c["stats"]["emoji"] += 1; save(c)
                    except: pass
                    return
        return

    # Fotoğraf
    if update.message.photo:
        fid = update.message.photo[-1].file_id
        bekle = context.user_data.get("bekle")
        if bekle == "join_foto":
            c["join_medya_tip"] = "foto"; c["join_medya_id"] = fid; save(c)
            context.user_data["bekle"] = None
            await update.message.reply_text("✅ Join fotoğrafı kaydedildi!", reply_markup=ana_kb())
        elif bekle == "oto_foto":
            c["oto_medya_tip"] = "foto"; c["oto_medya_id"] = fid; save(c)
            context.user_data["bekle"] = None
            await update.message.reply_text("✅ Oto fotoğraf kaydedildi!", reply_markup=ana_kb())
        return

    # Video
    if update.message.video:
        fid = update.message.video.file_id
        bekle = context.user_data.get("bekle")
        if bekle == "join_video":
            c["join_medya_tip"] = "video"; c["join_medya_id"] = fid; save(c)
            context.user_data["bekle"] = None
            await update.message.reply_text("✅ Join videosu kaydedildi!", reply_markup=ana_kb())
        elif bekle == "oto_video":
            c["oto_medya_tip"] = "video"; c["oto_medya_id"] = fid; save(c)
            context.user_data["bekle"] = None
            await update.message.reply_text("✅ Oto video kaydedildi!", reply_markup=ana_kb())
        return

    metin = update.message.text
    if not metin: return
    bekle = context.user_data.get("bekle")
    if not bekle: return

    if bekle == "kanal_ekle":
        try:
            parcalar = metin.strip().split("|")
            kid = int(parcalar[0].strip())
            isim = parcalar[1].strip() if len(parcalar) > 1 else str(kid)
            c["kanallar"].append({"id": kid, "isim": isim}); save(c)
            context.user_data["bekle"] = None
            await update.message.reply_text(f"✅ Eklendi: <b>{isim}</b>", parse_mode="HTML", reply_markup=ana_kb())
        except:
            await update.message.reply_text("❌ Format: <code>-1001234567890|Kanal Adı</code>", parse_mode="HTML")

    elif bekle == "join_mesaj":
        c["join_mesaj"] = metin; save(c); context.user_data["bekle"] = None
        await update.message.reply_text("✅ Mesaj güncellendi!", reply_markup=ana_kb())

    elif bekle == "join_buton":
        try:
            p = metin.strip().split("|")
            if "join_butonlar" not in c: c["join_butonlar"] = []
            c["join_butonlar"].append([p[0].strip(), p[1].strip()]); save(c)
            context.user_data["bekle"] = None
            await update.message.reply_text(f"✅ Buton eklendi: {p[0]}", reply_markup=ana_kb())
        except:
            await update.message.reply_text("❌ Format: <code>Buton Adı|https://link.com</code>", parse_mode="HTML")

    elif bekle == "oto_mesaj":
        c["oto_mesajlar"].append(metin); save(c); context.user_data["bekle"] = None
        await update.message.reply_text("✅ Mesaj eklendi!", reply_markup=ana_kb())

    elif bekle == "oto_aralik":
        try:
            c["oto_aralik"] = int(float(metin) * 3600); save(c); context.user_data["bekle"] = None
            await update.message.reply_text(f"✅ Aralık: {metin} saat", reply_markup=ana_kb())
        except:
            await update.message.reply_text("❌ Sayı gir. Örnek: 2")

    elif bekle == "emoji_kural":
        p = metin.strip().split()
        if len(p) >= 2:
            c["emoji_kurallar"][p[0].lower()] = p[1]; save(c); context.user_data["bekle"] = None
            await update.message.reply_text(f"✅ Kural: <b>{p[0]}</b> → {p[1]}", parse_mode="HTML", reply_markup=ana_kb())
        else:
            await update.message.reply_text("❌ Format: <code>kelime 😀</code>", parse_mode="HTML")

    elif bekle == "captcha_sure":
        try:
            c["captcha_sure"] = int(metin); save(c); context.user_data["bekle"] = None
            await update.message.reply_text(f"✅ Süre: {metin} saniye", reply_markup=ana_kb())
        except:
            await update.message.reply_text("❌ Sayı gir. Örnek: 120")

    elif bekle == "rss_url":
        c["rss_url"] = metin.strip(); save(c); context.user_data["bekle"] = None
        await update.message.reply_text(f"✅ RSS URL kaydedildi!", reply_markup=ana_kb())

    elif bekle == "rss_aralik":
        try:
            c["rss_aralik"] = int(metin) * 60; save(c); context.user_data["bekle"] = None
            await update.message.reply_text(f"✅ RSS aralığı: {metin} dakika", reply_markup=ana_kb())
        except:
            await update.message.reply_text("❌ Sayı gir.")

    elif bekle == "uyelik_fiyat":
        try:
            p = metin.strip().split("|")
            plan, fiyat = p[0].strip(), int(p[1].strip())
            if plan in c["uyelik_fiyatlar"]:
                c["uyelik_fiyatlar"][plan]["fiyat"] = fiyat; save(c); context.user_data["bekle"] = None
                await update.message.reply_text(f"✅ {plan} fiyatı: {fiyat} USDT", reply_markup=ana_kb())
            else:
                await update.message.reply_text("❌ Plan: 1ay, 3ay veya yillik")
        except:
            await update.message.reply_text("❌ Format: <code>1ay|50</code>", parse_mode="HTML")

    elif bekle == "uyelik_cuzdan":
        try:
            p = metin.strip().split("|")
            tip, adres = p[0].strip().lower(), p[1].strip()
            if tip == "ton": c["uyelik_ton_adres"] = adres
            elif tip == "usdt": c["uyelik_usdt_adres"] = adres
            save(c); context.user_data["bekle"] = None
            await update.message.reply_text(f"✅ {tip.upper()} cüzdanı güncellendi!", reply_markup=ana_kb())
        except:
            await update.message.reply_text("❌ Format: <code>ton|ADRES</code>", parse_mode="HTML")

# ─── KOMUTLAR ──────────────────────────────────────────────────
async def iptal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["bekle"] = None
    await update.message.reply_text("❌ İptal.", reply_markup=ana_kb())

async def otosil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    c = cfg()
    if not context.args or not context.args[0].isdigit():
        return await update.message.reply_text("Kullanım: /otosil 2")
    idx = int(context.args[0]) - 1
    if 0 <= idx < len(c["oto_mesajlar"]):
        silinen = c["oto_mesajlar"].pop(idx); save(c)
        await update.message.reply_text(f"🗑 Silindi: {silinen}")
    else:
        await update.message.reply_text("❌ Geçersiz numara!")

async def emojisil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    c = cfg()
    if not context.args: return await update.message.reply_text("Kullanım: /emojisil kelime")
    k = context.args[0].lower()
    if k in c["emoji_kurallar"]:
        del c["emoji_kurallar"][k]; save(c)
        await update.message.reply_text(f"🗑 Silindi: {k}")
    else:
        await update.message.reply_text(f"❌ '{k}' bulunamadı!")

async def butonsil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    c = cfg()
    if not context.args or not context.args[0].isdigit():
        return await update.message.reply_text("Kullanım: /butonsil 1")
    idx = int(context.args[0]) - 1
    butonlar = c.get("join_butonlar", [])
    if 0 <= idx < len(butonlar):
        silinen = butonlar.pop(idx); c["join_butonlar"] = butonlar; save(c)
        await update.message.reply_text(f"🗑 Silindi: {silinen[0]}")
    else:
        await update.message.reply_text("❌ Geçersiz!")

async def onayla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if len(context.args) < 2:
        return await update.message.reply_text("Kullanım: /onayla [user_id] [1ay|3ay|yillik]")
    c = cfg()
    try:
        uid = context.args[0]
        plan = context.args[1]
        if plan not in c["uyelik_fiyatlar"]:
            return await update.message.reply_text("❌ Plan: 1ay, 3ay, yillik")
        gun = c["uyelik_fiyatlar"][plan]["gun"]
        bitis = (datetime.now() + timedelta(days=gun)).strftime("%Y-%m-%d")
        if "uyelikler" not in c: c["uyelikler"] = {}
        c["uyelikler"][uid] = {"plan": plan, "bitis": bitis, "aktif": True, "isim": f"Kullanıcı {uid}"}
        c["stats"]["uyelik_satis"] += 1; save(c)
        # Kanallara ekle
        for kanal in c["kanallar"]:
            try:
                await context.bot.unban_chat_member(kanal["id"], int(uid))
            except: pass
        await update.message.reply_text(f"✅ Üyelik onaylandı!\nKullanıcı: {uid}\nPlan: {plan}\nBitiş: {bitis}")
        try:
            await context.bot.send_message(
                chat_id=int(uid),
                text=f"✅ <b>Üyeliğin Onaylandı!</b>\n\nPlan: {c['uyelik_fiyatlar'][plan]['label']}\nBitiş: {bitis}\n\nHoş geldin! 🎉",
                parse_mode="HTML"
            )
        except: pass
    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {e}")

async def uye_ol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kullanıcıların üyelik satın alması için"""
    c = cfg()
    if not c["uyelik_aktif"]:
        return await update.message.reply_text("❌ Üyelik sistemi şu an aktif değil.")
    fiyatlar = c["uyelik_fiyatlar"]
    metin = (
        "💰 <b>Ücretli Üyelik</b>\n\n"
        + "\n".join([f"• {v['label']}: <b>{v['fiyat']} USDT</b>" for v in fiyatlar.values()])
        + f"\n\n<b>Ödeme Yöntemleri:</b>\n"
        f"💎 TON: <code>{c['uyelik_ton_adres']}</code>\n"
        f"💵 USDT (TRC20): <code>{c['uyelik_usdt_adres']}</code>\n\n"
        f"Ödeme yaptıktan sonra ekran görüntüsü ile @yonetici'ye ulaşın."
    )
    await update.message.reply_text(metin, parse_mode="HTML")

# ─── JOIN HANDLER ──────────────────────────────────────────────
async def join_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = cfg()
    if not c["join_aktif"]: return
    user = update.chat_join_request.from_user
    try:
        await _mesaj_gonder(
            context.bot, user.id,
            c["join_mesaj"].format(first_name=user.first_name or "Kullanıcı",
                                   last_name=user.last_name or "", username=user.username or ""),
            c.get("join_medya_tip","yok"), c.get("join_medya_id",""), c.get("join_butonlar",[])
        )
        await update.chat_join_request.approve()
        c["stats"]["join"] += 1
        b = c.get("buyume", {})
        gun = bugun()
        if gun not in b: b[gun] = {"katilan": 0}
        b[gun]["katilan"] += 1
        c["buyume"] = b; save(c)
        logger.info(f"✅ Join: {user.full_name}")
    except Exception as e:
        logger.error(f"Join hatası: {e}")
        try: await update.chat_join_request.approve()
        except: pass

# ─── YENİ ÜYE (CAPTCHA) ────────────────────────────────────────
async def yeni_uye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = cfg()
    if not c["captcha_aktif"]: return
    if not update.message or not update.message.new_chat_members: return
    for user in update.message.new_chat_members:
        if user.is_bot: continue
        a = random.randint(1, 10)
        b2 = random.randint(1, 10)
        cevap = a + b2
        c["captcha_bekleyenler"][str(user.id)] = {"cevap": cevap, "chat": update.effective_chat.id}
        save(c)
        await update.message.reply_text(
            f"👋 Hoş geldin {user.first_name}!\n\n"
            f"🔐 Devam etmek için şu soruyu cevapla:\n\n"
            f"<b>{a} + {b2} = ?</b>\n\n"
            f"⏱ {c['captcha_sure']} saniyeniz var.",
            parse_mode="HTML"
        )
        context.job_queue.run_once(
            captcha_sure_doldu,
            c["captcha_sure"],
            data={"user_id": user.id, "chat_id": update.effective_chat.id},
            name=f"captcha_{user.id}"
        )

async def captcha_sure_doldu(context):
    data = context.job.data
    c = cfg()
    uid = str(data["user_id"])
    if uid in c.get("captcha_bekleyenler", {}):
        del c["captcha_bekleyenler"][uid]; save(c)
        try:
            await context.bot.ban_chat_member(data["chat_id"], data["user_id"])
            await context.bot.unban_chat_member(data["chat_id"], data["user_id"])
            await context.bot.send_message(data["chat_id"], f"⏱ Süre doldu, kullanıcı gruptan çıkarıldı.")
        except Exception as e:
            logger.error(f"Captcha ban hatası: {e}")

# ─── RSS JOB ───────────────────────────────────────────────────
async def rss_kontrol(context):
    c = cfg()
    if not c["rss_aktif"] or not c.get("rss_url") or not c.get("rss_kanal"): return
    try:
        feed = feedparser.parse(c["rss_url"])
        if not feed.entries: return
        son = feed.entries[0]
        link = son.get("link", "")
        if link == c.get("rss_son_link"): return
        baslik = son.get("title", "Yeni Haber")
        ozet = son.get("summary", "")[:300]
        metin = f"📰 <b>{baslik}</b>\n\n{ozet}\n\n🔗 {link}"
        await context.bot.send_message(chat_id=c["rss_kanal"], text=metin, parse_mode="HTML")
        c["rss_son_link"] = link; save(c)
        logger.info(f"✅ RSS yayınlandı: {baslik}")
    except Exception as e:
        logger.error(f"RSS hatası: {e}")

# ─── OTO MESAJ JOB ─────────────────────────────────────────────
async def oto_job(context):
    c = cfg()
    if not c["oto_aktif"] or not c["oto_mesajlar"] or not c["kanallar"]: return
    mesaj = random.choice(c["oto_mesajlar"])
    for k in c["kanallar"]:
        try:
            await _mesaj_gonder(context.bot, k["id"], mesaj, c.get("oto_medya_tip","yok"), c.get("oto_medya_id",""))
            c["stats"]["oto"] += 1
        except Exception as e: logger.error(f"Oto hatası: {e}")
    save(c)

# ─── MAIN ──────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("iptal", iptal))
    app.add_handler(CommandHandler("otosil", otosil))
    app.add_handler(CommandHandler("emojisil", emojisil))
    app.add_handler(CommandHandler("butonsil", butonsil))
    app.add_handler(CommandHandler("onayla", onayla))
    app.add_handler(CommandHandler("uyeol", uye_ol))
    app.add_handler(CallbackQueryHandler(cb))
    app.add_handler(ChatJoinRequestHandler(join_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, yeni_uye))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, mesaj_handler))
    app.job_queue.run_repeating(oto_job, interval=3600, first=60)
    app.job_queue.run_repeating(rss_kontrol, interval=3600, first=120)
    print("🚀 Ana Bot v3.0 başlatıldı!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
