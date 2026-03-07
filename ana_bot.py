"""
╔══════════════════════════════════════════════════════════════════╗
║         TG SUITE PRO — v5.0                                     ║
║  Casino + Moderasyon + Topluluk + Yönetim                       ║
╚══════════════════════════════════════════════════════════════════╝
"""
import logging, random, json, os, asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Poll
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ChatJoinRequestHandler, ContextTypes, filters
)

BOT_TOKEN = "8743351745:AAGgX51IjWqSxNC6HY8yLINyabZ_4Dfq_Ow"
CONFIG    = "config.json"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT = {
    # Lisans
    "lisans": {"aktif": True, "plan": "pro", "bitis": ""},
    "adminler": [],
    "marka_isim": "TG Suite Pro",
    # Kanallar
    "kanallar": [],
    # Join bot
    "join_aktif": True,
    "join_medya_tip": "yok", "join_medya_id": "",
    "join_mesaj": "👋 Merhaba <b>{first_name}</b>!\n\nHoş geldin! 🎉",
    "join_butonlar": [],
    # Oto mesaj
    "oto_aktif": False, "oto_aralik": 3600,
    "oto_mesajlar": ["📢 Kanalımıza hoş geldiniz!"],
    "oto_medya_tip": "yok", "oto_medya_id": "",
    # Emoji
    "emoji_aktif": True,
    "emoji_kurallar": {"merhaba": "👋", "teşekkür": "🙏", "harika": "🔥"},
    # Captcha
    "captcha_aktif": False, "captcha_sure": 120, "captcha_bekleyenler": {},
    # RSS
    "rss_aktif": False, "rss_url": "", "rss_kanal": None,
    "rss_aralik": 3600, "rss_son_link": "",
    # Çapraz
    "capraz_aktif": False, "capraz_kaynak": None, "capraz_hedefler": [],
    # Ücretli üyelik
    "uyelik_aktif": False,
    "uyelik_fiyatlar": {
        "1ay":    {"fiyat": 50,  "label": "1 Aylık",  "gun": 30},
        "3ay":    {"fiyat": 120, "label": "3 Aylık",  "gun": 90},
        "yillik": {"fiyat": 400, "label": "Yıllık",   "gun": 365}
    },
    "uyelik_ton_adres": "", "uyelik_usdt_adres": "",
    "uyelikler": {},
    # ── MODERASYOn ──
    "mod_aktif": True,
    "uyarilar": {},          # {user_id: sayi}
    "max_uyari": 3,          # kaçıncı uyarıda ban
    "yasakli_kelimeler": [], # bu kelimeleri içeren mesaj silinir
    "flood_aktif": False,
    "flood_limit": 5,        # X saniyede
    "flood_sure": 5,         # Y mesaj
    "flood_sayac": {},       # {user_id: [timestamp...]}
    "kurallar": "Henüz kural eklenmedi.",
    # ── REFERANS ──
    "ref_aktif": True,
    "ref_odul": 10,          # davet başına puan
    "ref_kayitlar": {},      # {davet_eden: [davet_edilen...]}
    # ── BAKİYE & PUAN ──
    "bakiye_aktif": True,
    "bakiyeler": {},         # {user_id: {"puan": 0, "isim": ""}}
    "gunluk_bonus": 50,
    "gunluk_bonus_al": {},   # {user_id: "2024-01-01"}
    # ── CASİNO ──
    "casino_aktif": True,
    "casino_min_bahis": 10,
    "casino_max_bahis": 1000,
    # ── ETKİNLİK & ANKET ──
    "etkinlikler": {},
    # ── KRİPTO ──
    "kripto_aktif": True,
    # ── TİCKET ──
    "tickets": {},
    # ── İSTATİSTİK ──
    "buyume": {},
    "stats": {"join": 0, "oto": 0, "emoji": 0, "uyelik_satis": 0, "casino_oyun": 0}
}

# ── CONFIG ──────────────────────────────────────────────────────
def cfg():
    if os.path.exists(CONFIG):
        try:
            with open(CONFIG, encoding="utf-8") as f:
                data = json.load(f)
            for k, v in DEFAULT.items():
                if k not in data: data[k] = v
            return data
        except: pass
    save(DEFAULT.copy()); return DEFAULT.copy()

def save(c):
    with open(CONFIG, "w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False, indent=2)

def is_admin(uid):
    return uid in cfg().get("adminler", [])

def bugun(): return datetime.now().strftime("%Y-%m-%d")

def get_bakiye(c, uid):
    return c["bakiyeler"].setdefault(str(uid), {"puan": 0, "isim": "?"})

def add_puan(c, uid, isim, miktar):
    b = get_bakiye(c, uid)
    b["puan"] = max(0, b["puan"] + miktar)
    b["isim"] = isim
    save(c)
    return b["puan"]

# ── ANA MENÜ ────────────────────────────────────────────────────
def ana_kb(c=None):
    if c is None: c = cfg()
    j  = "🟢" if c["join_aktif"] else "🔴"
    o  = "🟢" if c["oto_aktif"] else "🔴"
    e  = "🟢" if c["emoji_aktif"] else "🔴"
    ca = "🟢" if c["captcha_aktif"] else "🔴"
    r  = "🟢" if c["rss_aktif"] else "🔴"
    u  = "🟢" if c["uyelik_aktif"] else "🔴"
    m  = "🟢" if c["mod_aktif"] else "🔴"
    cs = "🟢" if c["casino_aktif"] else "🔴"
    bk = "🟢" if c["bakiye_aktif"] else "🔴"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{j} Join Bot", callback_data="m_join"),
         InlineKeyboardButton(f"{o} Oto Mesaj", callback_data="m_oto")],
        [InlineKeyboardButton(f"{e} Emoji Bot", callback_data="m_emoji"),
         InlineKeyboardButton("📢 Kanallar", callback_data="m_kanal")],
        [InlineKeyboardButton(f"{ca} Captcha", callback_data="m_captcha"),
         InlineKeyboardButton(f"{r} RSS Bot", callback_data="m_rss")],
        [InlineKeyboardButton("📣 Çapraz Paylaşım", callback_data="m_capraz"),
         InlineKeyboardButton(f"{u} Ücretli Üyelik", callback_data="m_uyelik")],
        [InlineKeyboardButton(f"{m} Moderasyon", callback_data="m_mod"),
         InlineKeyboardButton(f"{cs} 🎰 Casino", callback_data="m_casino")],
        [InlineKeyboardButton(f"{bk} 💸 Bakiye/Puan", callback_data="m_bakiye"),
         InlineKeyboardButton("🤝 Referans", callback_data="m_ref")],
        [InlineKeyboardButton("📊 Etkinlik & Anket", callback_data="m_etkinlik"),
         InlineKeyboardButton("📈 Kripto Fiyat", callback_data="m_kripto")],
        [InlineKeyboardButton("🎫 Destek Tickets", callback_data="m_ticket"),
         InlineKeyboardButton("📊 İstatistik", callback_data="m_stat")],
        [InlineKeyboardButton("🎨 Marka & Admin", callback_data="m_ayar")],
    ])

def geri_kb(cb): return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data=cb)]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    c = cfg()
    if not c["adminler"]:
        c["adminler"].append(uid); save(c)
    if not is_admin(uid):
        return await update.message.reply_text("❌ Erişim yok.")
    await update.message.reply_text(
        f"⚡ <b>{c.get('marka_isim','TG Suite Pro')}</b>\n\n"
        f"📢 Kanal: {len(c['kanallar'])}  👥 Üye: {sum(1 for v in c['uyelikler'].values() if v.get('aktif'))}\n"
        f"💸 Bakiye kayıtlı: {len(c['bakiyeler'])}  🎰 Oyun: {c['stats']['casino_oyun']}",
        parse_mode="HTML", reply_markup=ana_kb(c)
    )

async def ana_goster(query, c=None):
    if c is None: c = cfg()
    await query.edit_message_text(
        f"⚡ <b>{c.get('marka_isim','TG Suite Pro')}</b>\n\n"
        f"📢 Kanal: {len(c['kanallar'])}  👥 Üye: {sum(1 for v in c['uyelikler'].values() if v.get('aktif'))}\n"
        f"💸 Bakiye kayıtlı: {len(c['bakiyeler'])}  🎰 Oyun: {c['stats']['casino_oyun']}",
        parse_mode="HTML", reply_markup=ana_kb(c)
    )

# ── YARDIMCI ────────────────────────────────────────────────────
async def _gonder(bot, chat_id, metin, mt="yok", mid="", butonlar=None):
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(b[0], url=b[1])] for b in butonlar]) if butonlar else None
    if mt == "foto" and mid: await bot.send_photo(chat_id=chat_id, photo=mid, caption=metin, parse_mode="HTML", reply_markup=kb)
    elif mt == "video" and mid: await bot.send_video(chat_id=chat_id, video=mid, caption=metin, parse_mode="HTML", reply_markup=kb)
    else: await bot.send_message(chat_id=chat_id, text=metin, parse_mode="HTML", reply_markup=kb)

# ── CALLBACK ────────────────────────────────────────────────────
async def cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if not is_admin(q.from_user.id): return await q.answer("❌ Yetki yok!", show_alert=True)
    d = q.data
    c = cfg()

    if d == "ana": await ana_goster(q)

    # KANAL
    elif d == "m_kanal":
        rows = [[InlineKeyboardButton(f"❌ {k['isim']}", callback_data=f"kanal_sil_{i}")] for i, k in enumerate(c["kanallar"])]
        rows += [[InlineKeyboardButton("➕ Ekle", callback_data="kanal_ekle")],[InlineKeyboardButton("🔙 Geri", callback_data="ana")]]
        liste = "\n".join([f"• {k['isim']} (<code>{k['id']}</code>)" for k in c["kanallar"]]) or "Kanal yok."
        await q.edit_message_text(f"📢 <b>Kanallar</b>\n\n{liste}", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(rows))
    elif d == "kanal_ekle":
        await q.edit_message_text("Format: <code>-1001234|Kanal Adı</code>\n\nİptal: /iptal", parse_mode="HTML", reply_markup=geri_kb("m_kanal"))
        context.user_data["bekle"] = "kanal_ekle"
    elif d.startswith("kanal_sil_"):
        idx=int(d.split("_")[-1])
        if 0<=idx<len(c["kanallar"]): c["kanallar"].pop(idx); save(c)
        await cb(update, context)

    # JOIN
    elif d == "m_join":
        await q.edit_message_text(
            f"✉️ <b>Join Request Bot</b>\n\nDurum: {'🟢' if c['join_aktif'] else '🔴'}\nMedya: {c.get('join_medya_tip','yok')}\nButon: {len(c.get('join_butonlar',[]))}",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔴 Kapat" if c["join_aktif"] else "🟢 Aç", callback_data="join_toggle")],
                [InlineKeyboardButton("✏️ Mesaj", callback_data="join_mesaj_duzenle"), InlineKeyboardButton("👁 Gör", callback_data="join_mesaj_gor")],
                [InlineKeyboardButton("🖼 Foto Ekle", callback_data="join_foto_ekle"), InlineKeyboardButton("🎬 Video Ekle", callback_data="join_video_ekle")],
                [InlineKeyboardButton("🔘 Buton Ekle", callback_data="join_buton_ekle"), InlineKeyboardButton("📋 Butonlar", callback_data="join_buton_gor")],
                [InlineKeyboardButton("🗑 Medyayı Kaldır", callback_data="join_medya_kaldir")],
                [InlineKeyboardButton("🔙 Geri", callback_data="ana")],
            ])
        )
    elif d=="join_toggle": c["join_aktif"]=not c["join_aktif"]; save(c); await cb(update,context)
    elif d=="join_mesaj_gor": await q.edit_message_text(f"📝 Mesaj:\n\n{c['join_mesaj']}", parse_mode="HTML", reply_markup=geri_kb("m_join"))
    elif d=="join_mesaj_duzenle": await q.edit_message_text("✏️ Yeni mesaj yaz:\n<code>{first_name}</code>=isim\n\nİptal: /iptal", parse_mode="HTML", reply_markup=geri_kb("m_join")); context.user_data["bekle"]="join_mesaj"
    elif d=="join_foto_ekle": await q.edit_message_text("📸 Fotoğrafı gönder:", reply_markup=geri_kb("m_join")); context.user_data["bekle"]="join_foto"
    elif d=="join_video_ekle": await q.edit_message_text("🎬 Videoyu gönder:", reply_markup=geri_kb("m_join")); context.user_data["bekle"]="join_video"
    elif d=="join_medya_kaldir": c["join_medya_tip"]="yok"; c["join_medya_id"]=""; save(c); await q.answer("✅ Kaldırıldı!", show_alert=True); await cb(update,context)
    elif d=="join_buton_ekle": await q.edit_message_text("Format: <code>Buton|https://link</code>\n\nİptal: /iptal", parse_mode="HTML", reply_markup=geri_kb("m_join")); context.user_data["bekle"]="join_buton"
    elif d=="join_buton_gor":
        txt="\n".join([f"{i+1}. {b[0]}" for i,b in enumerate(c.get("join_butonlar",[]))]) or "Buton yok."
        await q.edit_message_text(f"🔘 Butonlar:\n\n{txt}\n\nSilmek: /butonsil [no]", parse_mode="HTML", reply_markup=geri_kb("m_join"))

    # OTO MESAJ
    elif d == "m_oto":
        await q.edit_message_text(
            f"🤖 <b>Otomatik Mesaj</b>\n\nDurum: {'🟢' if c['oto_aktif'] else '🔴'}\n⏱ {c['oto_aralik']/3600:.1f}s\n📝 {len(c['oto_mesajlar'])} mesaj",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔴 Kapat" if c["oto_aktif"] else "🟢 Aç", callback_data="oto_toggle")],
                [InlineKeyboardButton("➕ Mesaj Ekle", callback_data="oto_ekle"), InlineKeyboardButton("📋 Listele", callback_data="oto_liste")],
                [InlineKeyboardButton("🖼 Foto Ekle", callback_data="oto_foto_ekle"), InlineKeyboardButton("🎬 Video Ekle", callback_data="oto_video_ekle")],
                [InlineKeyboardButton("⏱ Aralık", callback_data="oto_aralik"), InlineKeyboardButton("📤 Şimdi Gönder", callback_data="oto_simdi")],
                [InlineKeyboardButton("🗑 Medyayı Kaldır", callback_data="oto_medya_kaldir")],
                [InlineKeyboardButton("🔙 Geri", callback_data="ana")],
            ])
        )
    elif d=="oto_toggle": c["oto_aktif"]=not c["oto_aktif"]; save(c); await cb(update,context)
    elif d=="oto_ekle": await q.edit_message_text("➕ Mesajı yaz:\n\nİptal: /iptal", reply_markup=geri_kb("m_oto")); context.user_data["bekle"]="oto_mesaj"
    elif d=="oto_liste":
        txt="\n\n".join([f"<b>{i+1}.</b> {m}" for i,m in enumerate(c["oto_mesajlar"])]) or "Mesaj yok."
        await q.edit_message_text(f"📋 Mesajlar:\n\n{txt}\n\nSilmek: /otosil [no]", parse_mode="HTML", reply_markup=geri_kb("m_oto"))
    elif d=="oto_foto_ekle": await q.edit_message_text("📸 Fotoğrafı gönder:", reply_markup=geri_kb("m_oto")); context.user_data["bekle"]="oto_foto"
    elif d=="oto_video_ekle": await q.edit_message_text("🎬 Videoyu gönder:", reply_markup=geri_kb("m_oto")); context.user_data["bekle"]="oto_video"
    elif d=="oto_medya_kaldir": c["oto_medya_tip"]="yok"; c["oto_medya_id"]=""; save(c); await q.answer("✅ Kaldırıldı!", show_alert=True); await cb(update,context)
    elif d=="oto_aralik": await q.edit_message_text("⏱ Kaç saat? (örn: 2)\n\nİptal: /iptal", reply_markup=geri_kb("m_oto")); context.user_data["bekle"]="oto_aralik"
    elif d=="oto_simdi":
        if not c["oto_mesajlar"] or not c["kanallar"]: return await q.answer("❌ Mesaj/kanal yok!", show_alert=True)
        mesaj=random.choice(c["oto_mesajlar"]); basarili=0
        for k in c["kanallar"]:
            try: await _gonder(context.bot, k["id"], mesaj, c.get("oto_medya_tip","yok"), c.get("oto_medya_id","")); basarili+=1
            except: pass
        c["stats"]["oto"]+=basarili; save(c)
        await q.answer(f"✅ {basarili} kanala gönderildi!", show_alert=True)

    # EMOJİ
    elif d == "m_emoji":
        await q.edit_message_text(f"😀 <b>Emoji Bot</b>\n\nDurum: {'🟢' if c['emoji_aktif'] else '🔴'}\nKural: {len(c['emoji_kurallar'])}", parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔴 Kapat" if c["emoji_aktif"] else "🟢 Aç", callback_data="emoji_toggle")],
                [InlineKeyboardButton("➕ Kural Ekle", callback_data="emoji_ekle"), InlineKeyboardButton("📋 Kurallar", callback_data="emoji_liste")],
                [InlineKeyboardButton("🔙 Geri", callback_data="ana")],
            ]))
    elif d=="emoji_toggle": c["emoji_aktif"]=not c["emoji_aktif"]; save(c); await cb(update,context)
    elif d=="emoji_ekle": await q.edit_message_text("Format: <code>kelime 😀</code>\n\nİptal: /iptal", parse_mode="HTML", reply_markup=geri_kb("m_emoji")); context.user_data["bekle"]="emoji_kural"
    elif d=="emoji_liste":
        txt="\n".join([f"<b>{k}</b>→{v}" for k,v in c["emoji_kurallar"].items()]) or "Kural yok."
        await q.edit_message_text(f"📋 Kurallar:\n\n{txt}\n\nSilmek: /emojisil [kelime]", parse_mode="HTML", reply_markup=geri_kb("m_emoji"))

    # CAPTCHA
    elif d == "m_captcha":
        await q.edit_message_text(f"🔐 <b>Captcha</b>\n\nDurum: {'🟢' if c['captcha_aktif'] else '🔴'}\n⏱ {c['captcha_sure']}s", parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔴 Kapat" if c["captcha_aktif"] else "🟢 Aç", callback_data="captcha_toggle")],
                [InlineKeyboardButton("⏱ Süre Değiştir", callback_data="captcha_sure_degistir")],
                [InlineKeyboardButton("🔙 Geri", callback_data="ana")],
            ]))
    elif d=="captcha_toggle": c["captcha_aktif"]=not c["captcha_aktif"]; save(c); await cb(update,context)
    elif d=="captcha_sure_degistir": await q.edit_message_text("Kaç saniye?\n\nİptal: /iptal", reply_markup=geri_kb("m_captcha")); context.user_data["bekle"]="captcha_sure"

    # RSS
    elif d == "m_rss":
        kanal=next((k["isim"] for k in c["kanallar"] if k["id"]==c.get("rss_kanal")),"Seçilmedi")
        await q.edit_message_text(f"📰 <b>RSS Bot</b>\n\nDurum: {'🟢' if c['rss_aktif'] else '🔴'}\nURL: {c.get('rss_url') or '—'}\nKanal: {kanal}", parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔴 Kapat" if c["rss_aktif"] else "🟢 Aç", callback_data="rss_toggle")],
                [InlineKeyboardButton("🔗 URL Ayarla", callback_data="rss_url_ayarla"), InlineKeyboardButton("📢 Kanal Seç", callback_data="rss_kanal_sec")],
                [InlineKeyboardButton("🔙 Geri", callback_data="ana")],
            ]))
    elif d=="rss_toggle": c["rss_aktif"]=not c["rss_aktif"]; save(c); await cb(update,context)
    elif d=="rss_url_ayarla": await q.edit_message_text("RSS URL yaz:\n\nİptal: /iptal", reply_markup=geri_kb("m_rss")); context.user_data["bekle"]="rss_url"
    elif d=="rss_kanal_sec":
        if not c["kanallar"]: return await q.answer("❌ Kanal yok!", show_alert=True)
        rows=[[InlineKeyboardButton(k["isim"],callback_data=f"rss_k_{i}")] for i,k in enumerate(c["kanallar"])]+[[InlineKeyboardButton("🔙",callback_data="m_rss")]]
        await q.edit_message_text("Kanal seç:", reply_markup=InlineKeyboardMarkup(rows))
    elif d.startswith("rss_k_"):
        idx=int(d.split("_")[-1]); c["rss_kanal"]=c["kanallar"][idx]["id"]; save(c)
        await q.answer("✅ Seçildi!",show_alert=True); await cb(update,context)

    # ÇAPRAZ
    elif d == "m_capraz":
        kaynak=next((k["isim"] for k in c["kanallar"] if k["id"]==c.get("capraz_kaynak")),"Seçilmedi")
        hedefler=[k["isim"] for k in c["kanallar"] if k["id"] in c.get("capraz_hedefler",[])]
        await q.edit_message_text(f"📣 <b>Çapraz Paylaşım</b>\n\nDurum: {'🟢' if c['capraz_aktif'] else '🔴'}\nKaynak: {kaynak}\nHedef: {', '.join(hedefler) or '—'}", parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔴 Kapat" if c["capraz_aktif"] else "🟢 Aç", callback_data="capraz_toggle")],
                [InlineKeyboardButton("📥 Kaynak", callback_data="capraz_kaynak_sec"), InlineKeyboardButton("📤 Hedef", callback_data="capraz_hedef_sec")],
                [InlineKeyboardButton("🔙 Geri", callback_data="ana")],
            ]))
    elif d=="capraz_toggle": c["capraz_aktif"]=not c["capraz_aktif"]; save(c); await cb(update,context)
    elif d=="capraz_kaynak_sec":
        rows=[[InlineKeyboardButton(k["isim"],callback_data=f"capraz_k_{i}")] for i,k in enumerate(c["kanallar"])]+[[InlineKeyboardButton("🔙",callback_data="m_capraz")]]
        await q.edit_message_text("Kaynak seç:", reply_markup=InlineKeyboardMarkup(rows))
    elif d.startswith("capraz_k_"):
        idx=int(d.split("_")[-1]); c["capraz_kaynak"]=c["kanallar"][idx]["id"]; save(c)
        await q.answer("✅",show_alert=True); await cb(update,context)
    elif d=="capraz_hedef_sec":
        rows=[]
        for i,k in enumerate(c["kanallar"]):
            if k["id"]==c.get("capraz_kaynak"): continue
            s="✅" if k["id"] in c.get("capraz_hedefler",[]) else "◻️"
            rows.append([InlineKeyboardButton(f"{s} {k['isim']}",callback_data=f"capraz_h_{i}")])
        rows.append([InlineKeyboardButton("🔙",callback_data="m_capraz")])
        await q.edit_message_text("Hedefleri seç:", reply_markup=InlineKeyboardMarkup(rows))
    elif d.startswith("capraz_h_"):
        idx=int(d.split("_")[-1]); kid=c["kanallar"][idx]["id"]
        if "capraz_hedefler" not in c: c["capraz_hedefler"]=[]
        if kid in c["capraz_hedefler"]: c["capraz_hedefler"].remove(kid)
        else: c["capraz_hedefler"].append(kid)
        save(c); await cb(update,context)

    # ÜCRETLİ ÜYELİK
    elif d == "m_uyelik":
        aktif=sum(1 for v in c["uyelikler"].values() if v.get("aktif"))
        await q.edit_message_text(
            f"💰 <b>Ücretli Üyelik</b>\n\nDurum: {'🟢' if c['uyelik_aktif'] else '🔴'}\nAktif üye: {aktif}\n"
            +"\n".join([f"• {v['label']}: {v['fiyat']} USDT" for v in c['uyelik_fiyatlar'].values()]),
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔴 Kapat" if c["uyelik_aktif"] else "🟢 Aç",callback_data="uyelik_toggle")],
                [InlineKeyboardButton("💲 Fiyat",callback_data="uyelik_fiyat"), InlineKeyboardButton("👛 Cüzdan",callback_data="uyelik_cuzdan")],
                [InlineKeyboardButton("👥 Üyeler",callback_data="uyelik_liste"), InlineKeyboardButton("✅ Onayla",callback_data="uyelik_onayla_info")],
                [InlineKeyboardButton("🔙 Geri",callback_data="ana")],
            ]))
    elif d=="uyelik_toggle": c["uyelik_aktif"]=not c["uyelik_aktif"]; save(c); await cb(update,context)
    elif d=="uyelik_fiyat": await q.edit_message_text("Format: <code>1ay|50</code>\n\nİptal: /iptal", parse_mode="HTML", reply_markup=geri_kb("m_uyelik")); context.user_data["bekle"]="uyelik_fiyat"
    elif d=="uyelik_cuzdan": await q.edit_message_text("Format: <code>ton|ADRES</code>\n\nİptal: /iptal", parse_mode="HTML", reply_markup=geri_kb("m_uyelik")); context.user_data["bekle"]="uyelik_cuzdan"
    elif d=="uyelik_liste":
        uyelikler=[(uid2,v) for uid2,v in c["uyelikler"].items() if v.get("aktif")]
        txt="\n".join([f"👤 {v.get('isim','?')} — {v.get('plan','?')} — {v.get('bitis','?')}" for _,v in uyelikler]) or "Aktif üye yok."
        await q.edit_message_text(f"👥 Aktif Üyeler:\n\n{txt}", parse_mode="HTML", reply_markup=geri_kb("m_uyelik"))
    elif d=="uyelik_onayla_info": await q.edit_message_text("/onayla [user_id] [plan]\nÖrnek: /onayla 123 1ay", reply_markup=geri_kb("m_uyelik"))

    # MODERASYOn
    elif d == "m_mod":
        await q.edit_message_text(
            f"⚠️ <b>Moderasyon</b>\n\nDurum: {'🟢' if c['mod_aktif'] else '🔴'}\n"
            f"Max uyarı: {c['max_uyari']}\nYasaklı kelime: {len(c['yasakli_kelimeler'])}\n"
            f"Flood koruması: {'🟢' if c['flood_aktif'] else '🔴'}",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔴 Kapat" if c["mod_aktif"] else "🟢 Aç", callback_data="mod_toggle")],
                [InlineKeyboardButton("🔇 Flood Koru", callback_data="flood_toggle"),
                 InlineKeyboardButton("🚫 Yasaklı Kelime", callback_data="yasakli_menu")],
                [InlineKeyboardButton("⚠️ Max Uyarı Ayarla", callback_data="max_uyari_ayarla"),
                 InlineKeyboardButton("📌 Kuralları Düzenle", callback_data="kurallar_duzenle")],
                [InlineKeyboardButton("📋 Uyarı Listesi", callback_data="uyari_liste")],
                [InlineKeyboardButton("🔙 Geri", callback_data="ana")],
            ]))
    elif d=="mod_toggle": c["mod_aktif"]=not c["mod_aktif"]; save(c); await cb(update,context)
    elif d=="flood_toggle": c["flood_aktif"]=not c["flood_aktif"]; save(c); await cb(update,context)
    elif d=="yasakli_menu":
        txt="\n".join([f"• {k}" for k in c["yasakli_kelimeler"]]) or "Yasaklı kelime yok."
        await q.edit_message_text(f"🚫 <b>Yasaklı Kelimeler:</b>\n\n{txt}\n\nEkle: /yasakekle [kelime]\nSil: /yasaksil [kelime]", parse_mode="HTML", reply_markup=geri_kb("m_mod"))
    elif d=="max_uyari_ayarla": await q.edit_message_text("Max uyarı sayısını yaz (örn: 3):\n\nİptal: /iptal", reply_markup=geri_kb("m_mod")); context.user_data["bekle"]="max_uyari"
    elif d=="kurallar_duzenle": await q.edit_message_text("Yeni kuralları yaz:\n\nİptal: /iptal", reply_markup=geri_kb("m_mod")); context.user_data["bekle"]="kurallar"
    elif d=="uyari_liste":
        if c["uyarilar"]:
            txt="\n".join([f"ID {uid2}: {sayi} uyarı" for uid2,sayi in c["uyarilar"].items()])
        else: txt="Uyarı kaydı yok."
        await q.edit_message_text(f"⚠️ Uyarı Listesi:\n\n{txt}", reply_markup=geri_kb("m_mod"))

    # CASİNO
    elif d == "m_casino":
        await q.edit_message_text(
            f"🎰 <b>Casino Modülü</b>\n\nDurum: {'🟢' if c['casino_aktif'] else '🔴'}\n"
            f"Min bahis: {c['casino_min_bahis']} puan\nMax bahis: {c['casino_max_bahis']} puan\n\n"
            f"<b>Kullanıcı komutları:</b>\n"
            f"/zar [bahis] — Zar at\n/tura [bahis] — Yazı tura\n"
            f"/rulet [bahis] — Rulet\n/slot [bahis] — Slot makinesi\n/jackpot — Büyük ikramiye",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔴 Kapat" if c["casino_aktif"] else "🟢 Aç", callback_data="casino_toggle")],
                [InlineKeyboardButton("💰 Min Bahis", callback_data="casino_min"), InlineKeyboardButton("💎 Max Bahis", callback_data="casino_max")],
                [InlineKeyboardButton("🔙 Geri", callback_data="ana")],
            ]))
    elif d=="casino_toggle": c["casino_aktif"]=not c["casino_aktif"]; save(c); await cb(update,context)
    elif d=="casino_min": await q.edit_message_text("Min bahis miktarı (puan):\n\nİptal: /iptal", reply_markup=geri_kb("m_casino")); context.user_data["bekle"]="casino_min"
    elif d=="casino_max": await q.edit_message_text("Max bahis miktarı (puan):\n\nİptal: /iptal", reply_markup=geri_kb("m_casino")); context.user_data["bekle"]="casino_max"

    # BAKİYE
    elif d == "m_bakiye":
        top_puan=sum(v.get("puan",0) for v in c["bakiyeler"].values())
        await q.edit_message_text(
            f"💸 <b>Bakiye & Puan Sistemi</b>\n\nDurum: {'🟢' if c['bakiye_aktif'] else '🔴'}\n"
            f"Kayıtlı: {len(c['bakiyeler'])} kişi\nToplam puan: {top_puan:,}\n"
            f"Günlük bonus: {c['gunluk_bonus']} puan\n\n"
            f"<b>Kullanıcı komutları:</b>\n"
            f"/bakiye — Bakiyemi gör\n/bonus — Günlük bonus al\n"
            f"/transfer [kullanıcı] [miktar] — Transfer\n/top — Liderlik tablosu",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔴 Kapat" if c["bakiye_aktif"] else "🟢 Aç", callback_data="bakiye_toggle")],
                [InlineKeyboardButton("🎁 Bonus Ayarla", callback_data="bakiye_bonus"), InlineKeyboardButton("💸 Manuel Ver", callback_data="bakiye_ver")],
                [InlineKeyboardButton("🏆 Liderlik", callback_data="bakiye_top"), InlineKeyboardButton("🔄 Sıfırla", callback_data="bakiye_sifirla_onay")],
                [InlineKeyboardButton("🔙 Geri", callback_data="ana")],
            ]))
    elif d=="bakiye_toggle": c["bakiye_aktif"]=not c["bakiye_aktif"]; save(c); await cb(update,context)
    elif d=="bakiye_bonus": await q.edit_message_text("Günlük bonus miktarı (puan):\n\nİptal: /iptal", reply_markup=geri_kb("m_bakiye")); context.user_data["bekle"]="gunluk_bonus"
    elif d=="bakiye_ver": await q.edit_message_text("Format: <code>[user_id] [miktar]</code>\n\nİptal: /iptal", parse_mode="HTML", reply_markup=geri_kb("m_bakiye")); context.user_data["bekle"]="bakiye_ver"
    elif d=="bakiye_top":
        sirali=sorted(c["bakiyeler"].items(), key=lambda x: x[1].get("puan",0), reverse=True)[:10]
        txt="\n".join([f"{'🥇🥈🥉'[i] if i<3 else f'{i+1}.'} {v.get('isim','?')} — {v.get('puan',0):,} puan" for i,(uid2,v) in enumerate(sirali)]) or "Henüz kimse yok."
        await q.edit_message_text(f"🏆 <b>Liderlik Tablosu:</b>\n\n{txt}", parse_mode="HTML", reply_markup=geri_kb("m_bakiye"))
    elif d=="bakiye_sifirla_onay":
        await q.edit_message_text("⚠️ Tüm bakiyeleri sıfırlamak istediğine emin misin?", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Evet, Sıfırla", callback_data="bakiye_sifirla"), InlineKeyboardButton("❌ İptal", callback_data="m_bakiye")]]))
    elif d=="bakiye_sifirla": c["bakiyeler"]={};  save(c); await q.answer("✅ Tüm bakiyeler sıfırlandı!",show_alert=True); await cb(update,context)

    # REFERANS
    elif d == "m_ref":
        top_ref=sorted(c["ref_kayitlar"].items(), key=lambda x: len(x[1]), reverse=True)[:5]
        txt="\n".join([f"{i+1}. ID {uid2} — {len(davetler)} davet" for i,(uid2,davetler) in enumerate(top_ref)]) or "Henüz davet yok."
        await q.edit_message_text(
            f"🤝 <b>Referans Sistemi</b>\n\nDurum: {'🟢' if c['ref_aktif'] else '🔴'}\n"
            f"Davet başı ödül: {c['ref_odul']} puan\n\n"
            f"<b>Top Davetçiler:</b>\n{txt}\n\n"
            f"Kullanıcılar /ref ile davet linki alır",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔴 Kapat" if c["ref_aktif"] else "🟢 Aç", callback_data="ref_toggle")],
                [InlineKeyboardButton("💎 Ödül Ayarla", callback_data="ref_odul_ayarla")],
                [InlineKeyboardButton("🔙 Geri", callback_data="ana")],
            ]))
    elif d=="ref_toggle": c["ref_aktif"]=not c["ref_aktif"]; save(c); await cb(update,context)
    elif d=="ref_odul_ayarla": await q.edit_message_text("Davet başı ödül (puan):\n\nİptal: /iptal", reply_markup=geri_kb("m_ref")); context.user_data["bekle"]="ref_odul"

    # ETKİNLİK & ANKET
    elif d == "m_etkinlik":
        await q.edit_message_text(
            f"📊 <b>Etkinlik & Anket</b>\n\n"
            f"<b>Komutlar:</b>\n"
            f"/anket [soru] | [secenek1] | [secenek2]...\n"
            f"Örnek: /anket En iyi kanal?|A Kanalı|B Kanalı|C Kanalı\n\n"
            f"/etkinlik [başlık] | [açıklama] | [tarih]\n"
            f"Örnek: /etkinlik Turnuva|Büyük ödül!|2024-12-01",
            parse_mode="HTML", reply_markup=geri_kb("ana"))

    # KRİPTO
    elif d == "m_kripto":
        await q.edit_message_text(
            f"📈 <b>Kripto Fiyat Sorgulama</b>\n\nDurum: {'🟢' if c['kripto_aktif'] else '🔴'}\n\n"
            f"<b>Kullanıcı komutları:</b>\n"
            f"/btc — Bitcoin fiyatı\n/eth — Ethereum fiyatı\n/ton — TON fiyatı\n"
            f"/kripto [sembol] — Herhangi bir kripto\nÖrnek: /kripto sol",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔴 Kapat" if c["kripto_aktif"] else "🟢 Aç", callback_data="kripto_toggle")],
                [InlineKeyboardButton("🔙 Geri", callback_data="ana")],
            ]))
    elif d=="kripto_toggle": c["kripto_aktif"]=not c["kripto_aktif"]; save(c); await cb(update,context)

    # TİCKET
    elif d == "m_ticket":
        acik=sum(1 for t in c.get("tickets",{}).values() if t.get("durum")=="acik")
        await q.edit_message_text(f"🎫 <b>Destek Tickets</b>\n\nAçık: {acik}\n\n/destek [mesaj] ile ticket açılır\n/cevap [id] [mesaj] ile yanıtlanır",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 Açık Ticketlar", callback_data="ticket_liste")],
                [InlineKeyboardButton("🔙 Geri", callback_data="ana")],
            ]))
    elif d=="ticket_liste":
        tickets=[(tid,t) for tid,t in c.get("tickets",{}).items() if t.get("durum")=="acik"]
        txt="\n\n".join([f"🎫#{tid}\n{t.get('isim','?')}: {t.get('mesaj','?')[:80]}" for tid,t in tickets]) or "Açık ticket yok."
        await q.edit_message_text(f"📋 Açık Ticketlar:\n\n{txt}", reply_markup=geri_kb("m_ticket"))

    # AYARLAR
    elif d == "m_ayar":
        admin_txt="\n".join([f"• <code>{a}</code>" for a in c["adminler"]])
        await q.edit_message_text(f"⚙️ <b>Marka & Admin</b>\n\nBot adı: {c.get('marka_isim')}\nAdminler:\n{admin_txt}", parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✏️ Bot Adı", callback_data="marka_isim"), InlineKeyboardButton("➕ Admin Ekle", callback_data="admin_ekle")],
                [InlineKeyboardButton("➖ Admin Sil", callback_data="admin_sil_menu")],
                [InlineKeyboardButton("🔙 Geri", callback_data="ana")],
            ]))
    elif d=="marka_isim": await q.edit_message_text("Yeni bot adı yaz:\n\nİptal: /iptal", reply_markup=geri_kb("m_ayar")); context.user_data["bekle"]="marka_isim"
    elif d=="admin_ekle": await q.edit_message_text("Eklenecek admin ID'sini yaz:\n\nİptal: /iptal", reply_markup=geri_kb("m_ayar")); context.user_data["bekle"]="admin_ekle"
    elif d=="admin_sil_menu":
        rows=[[InlineKeyboardButton(f"❌ {a}",callback_data=f"admin_sil_{a}")] for a in c["adminler"]]
        rows.append([InlineKeyboardButton("🔙",callback_data="m_ayar")])
        await q.edit_message_text("Silinecek admini seç:", reply_markup=InlineKeyboardMarkup(rows))
    elif d.startswith("admin_sil_"):
        aid=int(d.split("_")[-1])
        if aid in c["adminler"] and len(c["adminler"])>1: c["adminler"].remove(aid); save(c); await q.answer("✅ Silindi!",show_alert=True)
        else: await q.answer("❌ Son admin silinemez!",show_alert=True)
        await cb(update,context)

    # İSTATİSTİK
    elif d == "m_stat":
        s=c["stats"]; b=c.get("buyume",{})
        haftalik=sum(v.get("katilan",0) for v in list(b.values())[-7:])
        top_casino=sorted(c["bakiyeler"].items(),key=lambda x:x[1].get("puan",0),reverse=True)
        en_zengin=f"{top_casino[0][1].get('isim','?')} — {top_casino[0][1].get('puan',0):,} puan" if top_casino else "—"
        await q.edit_message_text(
            f"📊 <b>İstatistik</b>\n\n"
            f"📈 Son 7 gün: +{haftalik} üye\n"
            f"✉️ Join: {s['join']}  🤖 Oto: {s['oto']}\n"
            f"🎰 Casino oyun: {s['casino_oyun']}\n"
            f"💸 Kayıtlı bakiye: {len(c['bakiyeler'])} kişi\n"
            f"🤝 Toplam davet: {sum(len(v) for v in c['ref_kayitlar'].values())}\n"
            f"🏆 En zengin: {en_zengin}",
            parse_mode="HTML", reply_markup=geri_kb("ana"))

# ── KULLANICI KOMUTLARI ─────────────────────────────────────────

# BAKİYE
async def bakiye_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c=cfg()
    if not c["bakiye_aktif"]: return
    uid=str(update.effective_user.id); isim=update.effective_user.first_name
    b=get_bakiye(c, uid)
    await update.message.reply_text(f"💸 <b>Bakiyen</b>\n\n💰 Puan: <b>{b['puan']:,}</b>\n\n/bonus ile günlük puan al!", parse_mode="HTML")

async def bonus_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c=cfg()
    if not c["bakiye_aktif"]: return
    uid=str(update.effective_user.id); isim=update.effective_user.first_name
    son=c["gunluk_bonus_al"].get(uid,"")
    if son==bugun():
        return await update.message.reply_text("❌ Bugün bonusunu aldın! Yarın tekrar gel 🕐")
    yeni=add_puan(c, uid, isim, c["gunluk_bonus"])
    c["gunluk_bonus_al"][uid]=bugun(); save(c)
    await update.message.reply_text(f"🎁 <b>Günlük Bonus!</b>\n\n+{c['gunluk_bonus']} puan kazandın!\n💰 Toplam: <b>{yeni:,}</b>", parse_mode="HTML")

async def transfer_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c=cfg()
    if not c["bakiye_aktif"]: return
    if len(context.args)<2: return await update.message.reply_text("Kullanım: /transfer @kullanıcı 100")
    uid=str(update.effective_user.id); isim=update.effective_user.first_name
    try:
        miktar=int(context.args[1])
        gonderen=get_bakiye(c, uid)
        if gonderen["puan"]<miktar: return await update.message.reply_text("❌ Yetersiz bakiye!")
        if miktar<=0: return await update.message.reply_text("❌ Geçersiz miktar!")
        # Hedef kullanıcıyı bul (reply veya @username)
        if update.message.reply_to_message:
            hedef_uid=str(update.message.reply_to_message.from_user.id)
            hedef_isim=update.message.reply_to_message.from_user.first_name
        else: return await update.message.reply_text("Transfer için bir mesajı yanıtla!")
        gonderen["puan"]-=miktar
        hedef=get_bakiye(c, hedef_uid); hedef["puan"]+=miktar; hedef["isim"]=hedef_isim
        save(c)
        await update.message.reply_text(f"✅ Transfer tamamlandı!\n{isim} → {hedef_isim}: <b>{miktar:,} puan</b>", parse_mode="HTML")
    except: await update.message.reply_text("❌ Hata! Kullanım: /transfer [miktar] (yanıtlayarak)")

async def top_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c=cfg()
    sirali=sorted(c["bakiyeler"].items(),key=lambda x:x[1].get("puan",0),reverse=True)[:10]
    madalya=["🥇","🥈","🥉"]
    txt="\n".join([f"{madalya[i] if i<3 else f'{i+1}.'} {v.get('isim','?')} — <b>{v.get('puan',0):,}</b>" for i,(uid2,v) in enumerate(sirali)]) or "Henüz kimse yok."
    await update.message.reply_text(f"🏆 <b>Liderlik Tablosu</b>\n\n{txt}", parse_mode="HTML")

# REFERANS
async def ref_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c=cfg()
    if not c["ref_aktif"]: return
    uid=str(update.effective_user.id)
    bot_info=await context.bot.get_me()
    link=f"https://t.me/{bot_info.username}?start=ref_{uid}"
    davetler=len(c["ref_kayitlar"].get(uid,[]))
    await update.message.reply_text(
        f"🤝 <b>Referans Linkin</b>\n\n<code>{link}</code>\n\n"
        f"Her davet → <b>{c['ref_odul']} puan</b>\n"
        f"Toplam davet: <b>{davetler}</b>",
        parse_mode="HTML")

# CASİNO — ZAR
async def zar_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c=cfg()
    if not c["casino_aktif"]: return
    uid=str(update.effective_user.id); isim=update.effective_user.first_name
    if not context.args: return await update.message.reply_text(f"🎲 Kullanım: /zar [bahis]\nMin: {c['casino_min_bahis']} | Max: {c['casino_max_bahis']}")
    try:
        bahis=int(context.args[0])
        b=get_bakiye(c, uid)
        if bahis<c["casino_min_bahis"]: return await update.message.reply_text(f"❌ Min bahis: {c['casino_min_bahis']} puan!")
        if bahis>c["casino_max_bahis"]: return await update.message.reply_text(f"❌ Max bahis: {c['casino_max_bahis']} puan!")
        if b["puan"]<bahis: return await update.message.reply_text(f"❌ Yetersiz bakiye! ({b['puan']:,} puan)")
        zar1=random.randint(1,6); zar2=random.randint(1,6)
        zar_emoji=["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣"]
        if zar1>zar2: kazanc=bahis; sonuc="🎉 Kazandın!"
        elif zar1<zar2: kazanc=-bahis; sonuc="😢 Kaybettin!"
        else: kazanc=int(bahis*1.5); sonuc="🎊 Beraberlik! Ekstra bonus!"
        yeni=add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"]+=1; save(c)
        await update.message.reply_text(
            f"🎲 <b>Zar Oyunu</b>\n\n"
            f"Sen: {zar_emoji[zar1-1]}  Bot: {zar_emoji[zar2-1]}\n\n"
            f"{sonuc}\n{'➕' if kazanc>0 else '➖'} <b>{abs(kazanc):,} puan</b>\n"
            f"💰 Bakiye: <b>{yeni:,}</b>", parse_mode="HTML")
    except: await update.message.reply_text("❌ Geçerli bir miktar gir!")

# CASİNO — YAZI TURA
async def tura_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c=cfg()
    if not c["casino_aktif"]: return
    uid=str(update.effective_user.id); isim=update.effective_user.first_name
    if not context.args: return await update.message.reply_text("Kullanım: /tura [bahis] yazı|tura")
    try:
        bahis=int(context.args[0]); tahmin=context.args[1].lower() if len(context.args)>1 else "yazı"
        b=get_bakiye(c, uid)
        if b["puan"]<bahis: return await update.message.reply_text("❌ Yetersiz bakiye!")
        if bahis<c["casino_min_bahis"] or bahis>c["casino_max_bahis"]: return await update.message.reply_text(f"❌ Bahis {c['casino_min_bahis']}-{c['casino_max_bahis']} arası olmalı!")
        sonuc=random.choice(["yazı","tura"])
        emoji="🪙" if sonuc=="yazı" else "💫"
        if tahmin==sonuc: kazanc=bahis; txt="🎉 Kazandın!"
        else: kazanc=-bahis; txt="😢 Kaybettin!"
        yeni=add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"]+=1; save(c)
        await update.message.reply_text(
            f"{emoji} <b>Yazı Tura</b>\n\nSonuç: <b>{sonuc.upper()}</b>\nTahmin: {tahmin}\n\n{txt}\n"
            f"{'➕' if kazanc>0 else '➖'} <b>{abs(kazanc):,} puan</b>\n💰 Bakiye: <b>{yeni:,}</b>", parse_mode="HTML")
    except: await update.message.reply_text("❌ Kullanım: /tura [bahis] yazı veya tura")

# CASİNO — SLOT
async def slot_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c=cfg()
    if not c["casino_aktif"]: return
    uid=str(update.effective_user.id); isim=update.effective_user.first_name
    if not context.args: return await update.message.reply_text(f"🎰 Kullanım: /slot [bahis]")
    try:
        bahis=int(context.args[0]); b=get_bakiye(c, uid)
        if b["puan"]<bahis: return await update.message.reply_text("❌ Yetersiz bakiye!")
        if bahis<c["casino_min_bahis"] or bahis>c["casino_max_bahis"]: return await update.message.reply_text(f"❌ Bahis {c['casino_min_bahis']}-{c['casino_max_bahis']} arası!")
        semboller=["🍒","🍋","🍊","🍇","⭐","💎","7️⃣"]
        s=[random.choice(semboller) for _ in range(3)]
        if s[0]==s[1]==s[2]=="7️⃣": kazanc=bahis*10; txt="🎊 JACKPOT! 10x!"
        elif s[0]==s[1]==s[2]=="💎": kazanc=bahis*5; txt="💎 ELMAS! 5x!"
        elif s[0]==s[1]==s[2]: kazanc=bahis*3; txt="🎉 3'lü! 3x!"
        elif s[0]==s[1] or s[1]==s[2]: kazanc=bahis; txt="✨ 2'li! 1x!"
        else: kazanc=-bahis; txt="😢 Kaybettin!"
        yeni=add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"]+=1; save(c)
        await update.message.reply_text(
            f"🎰 <b>Slot Makinesi</b>\n\n┌─────────┐\n│ {s[0]} {s[1]} {s[2]} │\n└─────────┘\n\n"
            f"{txt}\n{'➕' if kazanc>0 else '➖'} <b>{abs(kazanc):,} puan</b>\n💰 Bakiye: <b>{yeni:,}</b>", parse_mode="HTML")
    except: await update.message.reply_text("❌ Kullanım: /slot [bahis]")

# CASİNO — RULET
async def rulet_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c=cfg()
    if not c["casino_aktif"]: return
    uid=str(update.effective_user.id); isim=update.effective_user.first_name
    if len(context.args)<2: return await update.message.reply_text("🎡 Kullanım: /rulet [bahis] [kırmızı|siyah|tek|çift|0-36]")
    try:
        bahis=int(context.args[0]); tahmin=" ".join(context.args[1:]).lower()
        b=get_bakiye(c, uid)
        if b["puan"]<bahis: return await update.message.reply_text("❌ Yetersiz bakiye!")
        if bahis<c["casino_min_bahis"] or bahis>c["casino_max_bahis"]: return await update.message.reply_text(f"❌ Bahis {c['casino_min_bahis']}-{c['casino_max_bahis']} arası!")
        sayi=random.randint(0,36)
        kirmizi={1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
        renk="🔴 Kırmızı" if sayi in kirmizi else ("⚫ Siyah" if sayi>0 else "🟢 Sıfır")
        tek_cift="tek" if sayi%2==1 else "çift" if sayi>0 else "—"
        if tahmin==str(sayi): kazanc=bahis*35; txt=f"🎊 TAM İSABET! 35x!"
        elif tahmin in ["kırmızı","kirmizi"] and sayi in kirmizi: kazanc=bahis; txt="🔴 Kırmızı! Kazandın!"
        elif tahmin in ["siyah","siyahi"] and sayi>0 and sayi not in kirmizi: kazanc=bahis; txt="⚫ Siyah! Kazandın!"
        elif tahmin=="tek" and sayi%2==1: kazanc=bahis; txt="Tek! Kazandın!"
        elif tahmin=="çift" and sayi>0 and sayi%2==0: kazanc=bahis; txt="Çift! Kazandın!"
        else: kazanc=-bahis; txt="😢 Kaybettin!"
        yeni=add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"]+=1; save(c)
        await update.message.reply_text(
            f"🎡 <b>Rulet</b>\n\nSayı: <b>{sayi}</b> {renk}\n{'Tek/Çift: '+tek_cift if tek_cift!='—' else ''}\n\n"
            f"{txt}\n{'➕' if kazanc>0 else '➖'} <b>{abs(kazanc):,} puan</b>\n💰 Bakiye: <b>{yeni:,}</b>", parse_mode="HTML")
    except: await update.message.reply_text("❌ Kullanım: /rulet [bahis] kırmızı")

# MODERASYOn KOMUTLARI
async def warn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not update.message.reply_to_message: return await update.message.reply_text("Uyarmak için mesajı yanıtla!")
    c=cfg()
    hedef=update.message.reply_to_message.from_user
    uid=str(hedef.id)
    c["uyarilar"][uid]=c["uyarilar"].get(uid,0)+1
    sayi=c["uyarilar"][uid]; max_u=c["max_uyari"]
    save(c)
    if sayi>=max_u:
        try:
            await context.bot.ban_chat_member(update.effective_chat.id, hedef.id)
            c["uyarilar"].pop(uid,None); save(c)
            await update.message.reply_text(f"🔨 <b>{hedef.first_name}</b> banlandı! ({max_u}/{max_u} uyarı)", parse_mode="HTML")
        except Exception as e: await update.message.reply_text(f"❌ Ban başarısız: {e}")
    else:
        await update.message.reply_text(f"⚠️ <b>{hedef.first_name}</b> uyarıldı! ({sayi}/{max_u})", parse_mode="HTML")

async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not update.message.reply_to_message: return await update.message.reply_text("Banlamak için mesajı yanıtla!")
    hedef=update.message.reply_to_message.from_user
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, hedef.id)
        await update.message.reply_text(f"🔨 <b>{hedef.first_name}</b> banlandı!", parse_mode="HTML")
    except Exception as e: await update.message.reply_text(f"❌ {e}")

async def kick_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not update.message.reply_to_message: return await update.message.reply_text("Kicklemek için mesajı yanıtla!")
    hedef=update.message.reply_to_message.from_user
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, hedef.id)
        await context.bot.unban_chat_member(update.effective_chat.id, hedef.id)
        await update.message.reply_text(f"👟 <b>{hedef.first_name}</b> kicklendi!", parse_mode="HTML")
    except Exception as e: await update.message.reply_text(f"❌ {e}")

async def mute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not update.message.reply_to_message: return await update.message.reply_text("Mutlamak için mesajı yanıtla!")
    hedef=update.message.reply_to_message.from_user
    sure=int(context.args[0]) if context.args else 10
    try:
        until=datetime.now()+timedelta(minutes=sure)
        await context.bot.restrict_chat_member(update.effective_chat.id, hedef.id,
            permissions=ChatPermissions(can_send_messages=False), until_date=until)
        await update.message.reply_text(f"🔇 <b>{hedef.first_name}</b> {sure} dakika susturuldu!", parse_mode="HTML")
    except Exception as e: await update.message.reply_text(f"❌ {e}")

async def unmute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not update.message.reply_to_message: return
    hedef=update.message.reply_to_message.from_user
    try:
        await context.bot.restrict_chat_member(update.effective_chat.id, hedef.id,
            permissions=ChatPermissions(can_send_messages=True, can_send_media_messages=True,
                                        can_send_other_messages=True, can_add_web_page_previews=True))
        await update.message.reply_text(f"🔊 <b>{hedef.first_name}</b> sesi açıldı!", parse_mode="HTML")
    except Exception as e: await update.message.reply_text(f"❌ {e}")

async def kurallar_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c=cfg()
    await update.message.reply_text(f"📌 <b>Grup Kuralları</b>\n\n{c['kurallar']}", parse_mode="HTML")

async def yasakekle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not context.args: return await update.message.reply_text("Kullanım: /yasakekle kelime")
    c=cfg(); kelime=" ".join(context.args).lower()
    if kelime not in c["yasakli_kelimeler"]: c["yasakli_kelimeler"].append(kelime); save(c)
    await update.message.reply_text(f"✅ '{kelime}' yasaklı listeye eklendi!")

async def yasaksil_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not context.args: return await update.message.reply_text("Kullanım: /yasaksil kelime")
    c=cfg(); kelime=" ".join(context.args).lower()
    if kelime in c["yasakli_kelimeler"]: c["yasakli_kelimeler"].remove(kelime); save(c); await update.message.reply_text(f"✅ '{kelime}' kaldırıldı!")
    else: await update.message.reply_text("❌ Bulunamadı!")

# ANKET
async def anket_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not context.args: return await update.message.reply_text("Kullanım: /anket Soru?|Seçenek1|Seçenek2|Seçenek3")
    parcalar=" ".join(context.args).split("|")
    if len(parcalar)<3: return await update.message.reply_text("❌ En az 2 seçenek lazım!")
    soru=parcalar[0].strip(); secenekler=[p.strip() for p in parcalar[1:]]
    try:
        await context.bot.send_poll(update.effective_chat.id, soru, secenekler, is_anonymous=False)
    except Exception as e: await update.message.reply_text(f"❌ {e}")

# KRİPTO
async def kripto_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c=cfg()
    if not c["kripto_aktif"]: return
    sembol=context.args[0].upper() if context.args else "BTC"
    try:
        import urllib.request
        url=f"https://api.coingecko.com/api/v3/simple/price?ids={_kripto_id(sembol)}&vs_currencies=usd,try"
        with urllib.request.urlopen(url, timeout=5) as r:
            data=json.loads(r.read())
        kid=_kripto_id(sembol)
        if kid in data:
            usd=data[kid].get("usd","?"); try_val=data[kid].get("try","?")
            await update.message.reply_text(f"📈 <b>{sembol}</b>\n\n💵 ${usd:,}\n🇹🇷 ₺{try_val:,}", parse_mode="HTML")
        else: await update.message.reply_text(f"❌ '{sembol}' bulunamadı!")
    except Exception as e: await update.message.reply_text(f"❌ Fiyat alınamadı: {e}")

def _kripto_id(sembol):
    ids={"BTC":"bitcoin","ETH":"ethereum","TON":"the-open-network","SOL":"solana",
         "BNB":"binancecoin","USDT":"tether","XRP":"ripple","ADA":"cardano","DOT":"polkadot","AVAX":"avalanche-2"}
    return ids.get(sembol.upper(), sembol.lower())

async def btc_cmd(update, context): context.args=["BTC"]; await kripto_cmd(update, context)
async def eth_cmd(update, context): context.args=["ETH"]; await kripto_cmd(update, context)
async def ton_cmd(update, context): context.args=["TON"]; await kripto_cmd(update, context)

# TICKET & DESTEK
async def destek_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("Kullanım: /destek [mesajın]")
    c=cfg(); uid=update.effective_user.id
    tid=str(uid)[-6:]
    c.setdefault("tickets",{})[tid]={"durum":"acik","isim":update.effective_user.first_name,"user_id":uid,"mesaj":" ".join(context.args)}
    save(c)
    await update.message.reply_text(f"🎫 Ticket açıldı #{tid}\nEn kısa sürede yanıtlanacak!")
    for aid in c["adminler"]:
        try: await context.bot.send_message(aid, f"🎫 <b>Yeni Ticket #{tid}</b>\n👤 {update.effective_user.first_name} ({uid})\n💬 {' '.join(context.args)}\n\nCevap: /cevap {tid} [mesaj]", parse_mode="HTML")
        except: pass

async def cevap_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if len(context.args)<2: return await update.message.reply_text("Kullanım: /cevap [ticket_id] [mesaj]")
    c=cfg(); tid=context.args[0]; mesaj=" ".join(context.args[1:])
    if tid not in c.get("tickets",{}): return await update.message.reply_text("❌ Ticket bulunamadı!")
    ticket=c["tickets"][tid]; ticket["durum"]="kapali"; save(c)
    try:
        await context.bot.send_message(ticket["user_id"], f"🎫 <b>Ticket #{tid} Yanıtlandı</b>\n\n{mesaj}", parse_mode="HTML")
        await update.message.reply_text("✅ Yanıt gönderildi!")
    except: await update.message.reply_text("❌ Kullanıcıya ulaşılamadı!")

# ÜCRETLI ÜYELİK
async def onayla_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if len(context.args)<2: return await update.message.reply_text("Kullanım: /onayla [user_id] [1ay|3ay|yillik]")
    c=cfg()
    try:
        uid_str,plan=context.args[0],context.args[1]
        if plan not in c["uyelik_fiyatlar"]: return await update.message.reply_text("❌ Plan: 1ay, 3ay, yillik")
        gun=c["uyelik_fiyatlar"][plan]["gun"]
        bitis=(datetime.now()+timedelta(days=gun)).strftime("%Y-%m-%d")
        c["uyelikler"][uid_str]={"plan":plan,"bitis":bitis,"aktif":True,"isim":f"Kullanıcı {uid_str}"}
        c["stats"]["uyelik_satis"]+=1; save(c)
        await update.message.reply_text(f"✅ Onaylandı! {uid_str} → {plan} → {bitis}")
        try: await context.bot.send_message(int(uid_str), f"✅ Üyeliğin onaylandı!\nPlan: {plan}\nBitiş: {bitis} 🎉")
        except: pass
    except Exception as e: await update.message.reply_text(f"❌ {e}")

async def uyeol_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c=cfg()
    if not c["uyelik_aktif"]: return await update.message.reply_text("❌ Üyelik sistemi aktif değil.")
    txt=("💰 <b>Ücretli Üyelik</b>\n\n"
        +"\n".join([f"• {v['label']}: <b>{v['fiyat']} USDT</b>" for v in c['uyelik_fiyatlar'].values()])
        +f"\n\n💎 TON: <code>{c['uyelik_ton_adres']}</code>\n💵 USDT: <code>{c['uyelik_usdt_adres']}</code>\n\nÖdeme sonrası yöneticiye ulaşın.")
    await update.message.reply_text(txt, parse_mode="HTML")

# ── JOIN HANDLER ─────────────────────────────────────────────────
async def join_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c=cfg()
    if not c["join_aktif"]: return
    user=update.chat_join_request.from_user
    # Referans kontrolü
    if context.args and str(context.args[0]).startswith("ref_"):
        davet_eden=context.args[0].replace("ref_","")
        if "ref_kayitlar" not in c: c["ref_kayitlar"]={}
        kayit=c["ref_kayitlar"].setdefault(davet_eden,[])
        if str(user.id) not in kayit:
            kayit.append(str(user.id))
            add_puan(c, davet_eden, "?", c["ref_odul"])
    try:
        await _gonder(context.bot, user.id,
            c["join_mesaj"].format(first_name=user.first_name or "Kullanıcı",
                                   last_name=user.last_name or "", username=user.username or ""),
            c.get("join_medya_tip","yok"), c.get("join_medya_id",""), c.get("join_butonlar",[]))
        await update.chat_join_request.approve()
        c["stats"]["join"]+=1
        b=c.get("buyume",{}); gun=bugun()
        if gun not in b: b[gun]={"katilan":0}
        b[gun]["katilan"]+=1; c["buyume"]=b; save(c)
    except Exception as e:
        logger.error(f"Join: {e}")
        try: await update.chat_join_request.approve()
        except: pass

# ── MESAJ HANDLER ────────────────────────────────────────────────
async def mesaj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    uid=update.effective_user.id; c=cfg()

    # Foto/Video yükleme
    if update.message.photo:
        fid=update.message.photo[-1].file_id; bekle=context.user_data.get("bekle")
        if is_admin(uid):
            if bekle=="join_foto": c["join_medya_tip"]="foto"; c["join_medya_id"]=fid; save(c); context.user_data["bekle"]=None; await update.message.reply_text("✅ Kaydedildi!", reply_markup=ana_kb())
            elif bekle=="oto_foto": c["oto_medya_tip"]="foto"; c["oto_medya_id"]=fid; save(c); context.user_data["bekle"]=None; await update.message.reply_text("✅ Kaydedildi!", reply_markup=ana_kb())
        return

    if update.message.video:
        fid=update.message.video.file_id; bekle=context.user_data.get("bekle")
        if is_admin(uid):
            if bekle=="join_video": c["join_medya_tip"]="video"; c["join_medya_id"]=fid; save(c); context.user_data["bekle"]=None; await update.message.reply_text("✅ Kaydedildi!", reply_markup=ana_kb())
            elif bekle=="oto_video": c["oto_medya_tip"]="video"; c["oto_medya_id"]=fid; save(c); context.user_data["bekle"]=None; await update.message.reply_text("✅ Kaydedildi!", reply_markup=ana_kb())
        return

    metin=update.message.text
    if not metin: return

    # Yasaklı kelime kontrolü
    if c["mod_aktif"] and not is_admin(uid):
        for yasak in c.get("yasakli_kelimeler",[]):
            if yasak.lower() in metin.lower():
                try: await update.message.delete()
                except: pass
                await update.message.reply_to_message and None or None
                return

    # Flood kontrolü
    if c["flood_aktif"] and not is_admin(uid):
        simdi=datetime.now().timestamp()
        uid_str=str(uid)
        flood=c["flood_sayac"].setdefault(uid_str,[])
        flood=[t for t in flood if simdi-t<c["flood_sure"]]
        flood.append(simdi)
        c["flood_sayac"][uid_str]=flood; save(c)
        if len(flood)>=c["flood_limit"]:
            try:
                await context.bot.restrict_chat_member(update.effective_chat.id, uid,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=datetime.now()+timedelta(minutes=5))
                await update.message.reply_text(f"🔇 Flood! {update.effective_user.first_name} 5 dakika susturuldu.")
                c["flood_sayac"][uid_str]=[]; save(c)
            except: pass
            return

    # Captcha kontrolü
    if str(uid) in c.get("captcha_bekleyenler",{}):
        bkl=c["captcha_bekleyenler"][str(uid)]
        if metin.strip()==str(bkl["cevap"]):
            del c["captcha_bekleyenler"][str(uid)]; save(c)
            await update.message.reply_text("✅ Doğrulandın! 🎉")
        else: await update.message.reply_text("❌ Yanlış cevap!")
        return

    # Emoji bot
    if c["emoji_aktif"] and not is_admin(uid):
        for k,v in c["emoji_kurallar"].items():
            if k.lower() in metin.lower():
                try: await update.message.reply_text(v); c["stats"]["emoji"]+=1; save(c)
                except: pass
                return

    if not is_admin(uid): return
    bekle=context.user_data.get("bekle")
    if not bekle: return

    # Admin girişleri
    kaydetler={
        "join_mesaj":("join_mesaj",None,"✅ Mesaj güncellendi!"),
        "rss_url":("rss_url",None,"✅ RSS URL kaydedildi!"),
        "marka_isim":("marka_isim",None,"✅ İsim güncellendi!"),
        "kurallar":("kurallar",None,"✅ Kurallar güncellendi!"),
    }
    if bekle in kaydetler:
        key,_,msg=kaydetler[bekle]; c[key]=metin; save(c); context.user_data["bekle"]=None
        await update.message.reply_text(msg, reply_markup=ana_kb())
    elif bekle=="kanal_ekle":
        try:
            p=metin.strip().split("|")
            c["kanallar"].append({"id":int(p[0].strip()),"isim":p[1].strip() if len(p)>1 else p[0]}); save(c)
            context.user_data["bekle"]=None; await update.message.reply_text("✅ Kanal eklendi!", reply_markup=ana_kb())
        except: await update.message.reply_text("❌ Format: <code>-100xxx|Kanal Adı</code>", parse_mode="HTML")
    elif bekle=="join_buton":
        try:
            p=metin.strip().split("|"); c.setdefault("join_butonlar",[]).append([p[0].strip(),p[1].strip()]); save(c)
            context.user_data["bekle"]=None; await update.message.reply_text("✅ Buton eklendi!", reply_markup=ana_kb())
        except: await update.message.reply_text("❌ Format: <code>Buton|https://link</code>", parse_mode="HTML")
    elif bekle=="oto_mesaj":
        c["oto_mesajlar"].append(metin); save(c); context.user_data["bekle"]=None
        await update.message.reply_text("✅ Mesaj eklendi!", reply_markup=ana_kb())
    elif bekle=="oto_aralik":
        try: c["oto_aralik"]=int(float(metin)*3600); save(c); context.user_data["bekle"]=None; await update.message.reply_text(f"✅ {metin} saat", reply_markup=ana_kb())
        except: await update.message.reply_text("❌ Sayı gir.")
    elif bekle=="emoji_kural":
        p=metin.strip().split()
        if len(p)>=2: c["emoji_kurallar"][p[0].lower()]=p[1]; save(c); context.user_data["bekle"]=None; await update.message.reply_text(f"✅ {p[0]}→{p[1]}", reply_markup=ana_kb())
        else: await update.message.reply_text("❌ Format: <code>kelime 😀</code>", parse_mode="HTML")
    elif bekle=="captcha_sure":
        try: c["captcha_sure"]=int(metin); save(c); context.user_data["bekle"]=None; await update.message.reply_text(f"✅ {metin}s", reply_markup=ana_kb())
        except: await update.message.reply_text("❌ Sayı gir.")
    elif bekle=="max_uyari":
        try: c["max_uyari"]=int(metin); save(c); context.user_data["bekle"]=None; await update.message.reply_text(f"✅ Max uyarı: {metin}", reply_markup=ana_kb())
        except: await update.message.reply_text("❌ Sayı gir.")
    elif bekle=="casino_min":
        try: c["casino_min_bahis"]=int(metin); save(c); context.user_data["bekle"]=None; await update.message.reply_text(f"✅ Min bahis: {metin}", reply_markup=ana_kb())
        except: await update.message.reply_text("❌ Sayı gir.")
    elif bekle=="casino_max":
        try: c["casino_max_bahis"]=int(metin); save(c); context.user_data["bekle"]=None; await update.message.reply_text(f"✅ Max bahis: {metin}", reply_markup=ana_kb())
        except: await update.message.reply_text("❌ Sayı gir.")
    elif bekle=="gunluk_bonus":
        try: c["gunluk_bonus"]=int(metin); save(c); context.user_data["bekle"]=None; await update.message.reply_text(f"✅ Günlük bonus: {metin}", reply_markup=ana_kb())
        except: await update.message.reply_text("❌ Sayı gir.")
    elif bekle=="bakiye_ver":
        try:
            p=metin.strip().split(); uid2,miktar=p[0],int(p[1])
            yeni=add_puan(c, uid2, f"Kullanıcı {uid2}", miktar)
            context.user_data["bekle"]=None; await update.message.reply_text(f"✅ {uid2} → +{miktar} puan (Toplam: {yeni:,})", reply_markup=ana_kb())
        except: await update.message.reply_text("❌ Format: [user_id] [miktar]")
    elif bekle=="ref_odul":
        try: c["ref_odul"]=int(metin); save(c); context.user_data["bekle"]=None; await update.message.reply_text(f"✅ Ödül: {metin} puan", reply_markup=ana_kb())
        except: await update.message.reply_text("❌ Sayı gir.")
    elif bekle=="uyelik_fiyat":
        try:
            p=metin.strip().split("|"); plan,fiyat=p[0].strip(),int(p[1].strip())
            if plan in c["uyelik_fiyatlar"]: c["uyelik_fiyatlar"][plan]["fiyat"]=fiyat; save(c); context.user_data["bekle"]=None; await update.message.reply_text(f"✅ {plan}: {fiyat} USDT", reply_markup=ana_kb())
            else: await update.message.reply_text("❌ Plan: 1ay, 3ay veya yillik")
        except: await update.message.reply_text("❌ Format: <code>1ay|50</code>", parse_mode="HTML")
    elif bekle=="uyelik_cuzdan":
        try:
            p=metin.strip().split("|"); tip,adres=p[0].lower(),p[1].strip()
            if tip=="ton": c["uyelik_ton_adres"]=adres
            elif tip=="usdt": c["uyelik_usdt_adres"]=adres
            save(c); context.user_data["bekle"]=None; await update.message.reply_text(f"✅ {tip.upper()} güncellendi!", reply_markup=ana_kb())
        except: await update.message.reply_text("❌ Format: <code>ton|ADRES</code>", parse_mode="HTML")
    elif bekle=="admin_ekle":
        try:
            aid=int(metin.strip())
            if aid not in c["adminler"]: c["adminler"].append(aid); save(c)
            context.user_data["bekle"]=None; await update.message.reply_text(f"✅ Admin eklendi: {aid}", reply_markup=ana_kb())
        except: await update.message.reply_text("❌ Geçerli ID gir.")

# ── CAPTCHA YENİ ÜYE ─────────────────────────────────────────────
async def yeni_uye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c=cfg()
    if not c["captcha_aktif"] or not update.message.new_chat_members: return
    for user in update.message.new_chat_members:
        if user.is_bot: continue
        a=random.randint(1,10); b2=random.randint(1,10)
        c["captcha_bekleyenler"][str(user.id)]={"cevap":a+b2,"chat":update.effective_chat.id}; save(c)
        await update.message.reply_text(f"👋 {user.first_name}!\n\n🔐 <b>{a} + {b2} = ?</b>\n\n⏱ {c['captcha_sure']} saniye", parse_mode="HTML")
        context.job_queue.run_once(_captcha_timeout, c["captcha_sure"],
            data={"user_id":user.id,"chat_id":update.effective_chat.id}, name=f"cap_{user.id}")

async def _captcha_timeout(context):
    data=context.job.data; c=cfg(); uid=str(data["user_id"])
    if uid in c.get("captcha_bekleyenler",{}):
        del c["captcha_bekleyenler"][uid]; save(c)
        try:
            await context.bot.ban_chat_member(data["chat_id"], data["user_id"])
            await context.bot.unban_chat_member(data["chat_id"], data["user_id"])
            await context.bot.send_message(data["chat_id"], "⏱ Süre doldu, kullanıcı çıkarıldı.")
        except: pass

# ── OTO & RSS JOBS ───────────────────────────────────────────────
async def oto_job(context):
    c=cfg()
    if not c["oto_aktif"] or not c["oto_mesajlar"] or not c["kanallar"]: return
    mesaj=random.choice(c["oto_mesajlar"])
    for k in c["kanallar"]:
        try: await _gonder(context.bot, k["id"], mesaj, c.get("oto_medya_tip","yok"), c.get("oto_medya_id","")); c["stats"]["oto"]+=1
        except Exception as e: logger.error(f"Oto: {e}")
    save(c)

async def rss_job(context):
    c=cfg()
    if not c["rss_aktif"] or not c.get("rss_url") or not c.get("rss_kanal"): return
    try:
        import feedparser
        feed=feedparser.parse(c["rss_url"])
        if not feed.entries: return
        son=feed.entries[0]; link=son.get("link","")
        if link==c.get("rss_son_link"): return
        baslik=son.get("title","Yeni"); ozet=son.get("summary","")[:300]
        await context.bot.send_message(c["rss_kanal"], f"📰 <b>{baslik}</b>\n\n{ozet}\n\n🔗 {link}", parse_mode="HTML")
        c["rss_son_link"]=link; save(c)
    except Exception as e: logger.error(f"RSS: {e}")

# ── KOMUTLAR ─────────────────────────────────────────────────────
async def iptal(update, context): context.user_data["bekle"]=None; await update.message.reply_text("❌ İptal.", reply_markup=ana_kb())
async def otosil_cmd(update, context):
    if not is_admin(update.effective_user.id): return
    c=cfg()
    if not context.args or not context.args[0].isdigit(): return await update.message.reply_text("Kullanım: /otosil 2")
    idx=int(context.args[0])-1
    if 0<=idx<len(c["oto_mesajlar"]): c["oto_mesajlar"].pop(idx); save(c); await update.message.reply_text("🗑 Silindi!")
    else: await update.message.reply_text("❌ Geçersiz!")
async def emojisil_cmd(update, context):
    if not is_admin(update.effective_user.id): return
    c=cfg()
    if not context.args: return await update.message.reply_text("Kullanım: /emojisil kelime")
    k=context.args[0].lower()
    if k in c["emoji_kurallar"]: del c["emoji_kurallar"][k]; save(c); await update.message.reply_text(f"🗑 {k} silindi!")
    else: await update.message.reply_text("❌ Bulunamadı!")
async def butonsil_cmd(update, context):
    if not is_admin(update.effective_user.id): return
    c=cfg()
    if not context.args or not context.args[0].isdigit(): return await update.message.reply_text("Kullanım: /butonsil 1")
    idx=int(context.args[0])-1; b=c.get("join_butonlar",[])
    if 0<=idx<len(b): b.pop(idx); c["join_butonlar"]=b; save(c); await update.message.reply_text("🗑 Silindi!")

def main():
    app=Application.builder().token(BOT_TOKEN).build()
    # Admin
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("iptal", iptal))
    app.add_handler(CommandHandler("otosil", otosil_cmd))
    app.add_handler(CommandHandler("emojisil", emojisil_cmd))
    app.add_handler(CommandHandler("butonsil", butonsil_cmd))
    app.add_handler(CommandHandler("onayla", onayla_cmd))
    app.add_handler(CommandHandler("destek", destek_cmd))
    app.add_handler(CommandHandler("cevap", cevap_cmd))
    app.add_handler(CommandHandler("yasakekle", yasakekle_cmd))
    app.add_handler(CommandHandler("yasaksil", yasaksil_cmd))
    app.add_handler(CommandHandler("anket", anket_cmd))
    # Moderasyon
    app.add_handler(CommandHandler("warn", warn_cmd))
    app.add_handler(CommandHandler("ban", ban_cmd))
    app.add_handler(CommandHandler("kick", kick_cmd))
    app.add_handler(CommandHandler("mute", mute_cmd))
    app.add_handler(CommandHandler("unmute", unmute_cmd))
    app.add_handler(CommandHandler("kurallar", kurallar_cmd))
    # Kullanıcı
    app.add_handler(CommandHandler("bakiye", bakiye_cmd))
    app.add_handler(CommandHandler("bonus", bonus_cmd))
    app.add_handler(CommandHandler("transfer", transfer_cmd))
    app.add_handler(CommandHandler("top", top_cmd))
    app.add_handler(CommandHandler("ref", ref_cmd))
    app.add_handler(CommandHandler("uyeol", uyeol_cmd))
    # Casino
    app.add_handler(CommandHandler("zar", zar_cmd))
    app.add_handler(CommandHandler("tura", tura_cmd))
    app.add_handler(CommandHandler("slot", slot_cmd))
    app.add_handler(CommandHandler("rulet", rulet_cmd))
    # Kripto
    app.add_handler(CommandHandler("kripto", kripto_cmd))
    app.add_handler(CommandHandler("btc", btc_cmd))
    app.add_handler(CommandHandler("eth", eth_cmd))
    app.add_handler(CommandHandler("ton", ton_cmd))
    # Handlers
    app.add_handler(CallbackQueryHandler(cb))
    app.add_handler(ChatJoinRequestHandler(join_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, yeni_uye))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, mesaj_handler))
    app.job_queue.run_repeating(oto_job, interval=3600, first=60)
    app.job_queue.run_repeating(rss_job, interval=3600, first=120)
    print("🚀 TG Suite Pro v5.0 başlatıldı!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
