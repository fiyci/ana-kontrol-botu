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
    "kullanicilar": {},       # {uid: {isim, username, giris, son_aktif, dm_ok}}
    "toplu_mesaj_aktif": True,
    "bakiye_aktif": True,
    "bakiyeler": {},
    "gunluk_bonus": 100,
    "gunluk_bonus_al": {},
    "streak_bonus_katsayi": 20,
    "streak_max": 7,
    "streak_kayitlar": {},
    "haftalik_bonus": 500,
    "haftalik_bonus_al": {},
    "aktiflik_puan": 2,
    "seviye_esikleri": {"1":0,"2":500,"3":1500,"4":3000,"5":6000,"6":10000,"7":20000,"8":35000,"9":50000,"10":75000},
    "seviye_rozetleri": {"1":"Lv1","2":"Lv2","3":"Lv3","4":"Lv4","5":"Lv5","6":"Lv6","7":"Lv7","8":"Lv8","9":"Lv9","10":"Lv10"},
    "vip_esik": 10000,
    "vip_bonus_katsayi": 1.5,
    "transfer_min": 10,
    "puan_carpan": 1.0,
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

def kaydet_kullanici(c, user):
    """Botla etkileşime giren her kullanıcıyı kaydet (DM için)"""
    if not user or user.is_bot: return
    uid_str = str(user.id)
    kullanicilar = c.setdefault("kullanicilar", {})
    if uid_str not in kullanicilar:
        kullanicilar[uid_str] = {
            "isim": user.first_name or "?",
            "username": user.username or "",
            "giris": bugun(),
            "son_aktif": bugun(),
            "dm_ok": True,  # DM alabilir mi (hata alınırsa False yapılır)
        }
    else:
        kullanicilar[uid_str]["isim"] = user.first_name or kullanicilar[uid_str].get("isim","?")
        kullanicilar[uid_str]["username"] = user.username or ""
        kullanicilar[uid_str]["son_aktif"] = bugun()


def bahis_kontrol(c, uid, bahis_str):
    """Bahis validasyonu. (hata_mesaji, bahis) döner. Hata yoksa hata_mesaji=None"""
    try:
        bahis = int(bahis_str)
    except:
        return "Gecersiz bahis miktari! Sayi gir.", None
    if bahis <= 0:
        return "Bahis 0'dan buyuk olmali!", None
    cmin = c.get("casino_min_bahis", 10)
    cmax = c.get("casino_max_bahis", 1000)
    if bahis < cmin or bahis > cmax:
        return f"Bahis {cmin}-{cmax} arasinda olmali!", None
    b = get_bakiye(c, str(uid))
    if b["puan"] < bahis:
        return f"Yetersiz bakiye! Bakiyen: {b['puan']:,} puan\n/bonus veya /hbonus ile puan kazan.", None
    return None, bahis

async def casino_gorev_tetikle(context, c, uid, isim, kazandi, kazanc=0):
    """Casino sonrası görev tetikle + başarım kontrolü"""
    mesajlar = []
    # İlk oyun görevi
    if gorev_tamamla(c, uid, isim, "ilk_oyun"):
        mesajlar.append(f"🎮 <b>Görev Tamamlandı!</b> Kumar Kapısı +{GOREVLER['ilk_oyun']['puan']} puan!")
    # Günlük oyun sayacı
    oyun_sayi = gorev_ilerleme(c, uid, "oyun")
    if oyun_sayi >= GOREVLER["gunluk_oyun"].get("hedef", 3):
        if gorev_tamamla(c, uid, isim, "gunluk_oyun"):
            mesajlar.append(f"🎲 <b>Günlük Görev!</b> Kumar Adığı +{GOREVLER['gunluk_oyun']['puan']} puan!")
    if kazandi:
        # İlk kazanç
        if gorev_tamamla(c, uid, isim, "ilk_kazanc"):
            mesajlar.append(f"🏆 <b>Görev!</b> İlk Zafer +{GOREVLER['ilk_kazanc']['puan']} puan!")
        # Günlük kazanç
        if gorev_tamamla(c, uid, isim, "gunluk_kazanc"):
            mesajlar.append(f"🤑 <b>Günlük Görev!</b> Kazanan +{GOREVLER['gunluk_kazanc']['puan']} puan!")
        # Cesur başarımı (500+ tek kazanç)
        if kazanc >= 500 and kontrol_basarim(c, uid, isim, "cesur"):
            mesajlar.append("⚡ <b>BAŞARIM: Cesur!</b> 500+ puan tek kazanç!")
    save(c)
    return mesajlar

def bugun(): return datetime.now().strftime("%Y-%m-%d")

def get_bakiye(c, uid):
    return c["bakiyeler"].setdefault(str(uid), {"puan":0,"isim":"?","toplam":0,"seviye":1})

def hesapla_seviye(c, puan):
    e = c.get("seviye_esikleri",{"1":0,"2":500,"3":1500,"4":3000,"5":6000,"6":10000,"7":20000,"8":35000,"9":50000,"10":75000})
    sev = 1
    for s,esik in sorted(e.items(), key=lambda x: int(x[0])):
        if puan >= int(esik): sev = int(s)
    return sev

def sonraki_seviye(c, puan):
    e = c.get("seviye_esikleri",{"1":0,"2":500,"3":1500,"4":3000,"5":6000,"6":10000,"7":20000,"8":35000,"9":50000,"10":75000})
    for s,esik in sorted(e.items(), key=lambda x: int(x[0])):
        if int(esik) > puan: return int(esik), int(s)
    return None, 10

def is_vip(c, uid):
    b = get_bakiye(c, str(uid))
    return b["puan"] >= c.get("vip_esik", 10000)

def add_puan(c, uid, isim, miktar):
    b = get_bakiye(c, uid)
    carpan = c.get("puan_carpan", 1.0)
    if miktar > 0 and is_vip(c, str(uid)):
        carpan *= c.get("vip_bonus_katsayi", 1.5)
    gercek = int(miktar * carpan) if miktar > 0 else miktar
    b["puan"] = max(0, b["puan"] + gercek)
    if miktar > 0: b["toplam"] = b.get("toplam",0) + gercek
    b["isim"] = isim
    b["seviye"] = hesapla_seviye(c, b["puan"])
    save(c)
    return b["puan"]

def gorev_tamamla(c, uid, isim, gorev_id):
    """Görevi tamamla, puan ver. True döner = yeni tamamlandı"""
    if gorev_id not in GOREVLER: return False
    g = GOREVLER[gorev_id]
    tamamlananlar = c.setdefault("tamamlanan_gorevler", {}).setdefault(uid, {})
    tip = g.get("tip", "hic")
    onceki = tamamlananlar.get(gorev_id, "")
    if tip == "hic" and onceki: return False
    if tip == "gun" and onceki == bugun(): return False
    if tip == "hafta":
        hkey = datetime.now().strftime("%Y-W%W")
        if onceki == hkey: return False
        tamamlananlar[gorev_id] = hkey
    else:
        tamamlananlar[gorev_id] = bugun()
    if g["puan"] > 0:
        add_puan(c, uid, isim, g["puan"])
    return True

def kontrol_basarim(c, uid, isim, basarim_id):
    """Başarımı kontrol et ve ver"""
    kazanilan = c.setdefault("basarimlar", {}).setdefault(uid, [])
    if basarim_id not in kazanilan:
        kazanilan.append(basarim_id)
        return True
    return False

def gorev_ilerleme(c, uid, tip_key, artir=1):
    """Günlük ilerleme sayacı (mesaj, oyun vb.)"""
    bugun_key = bugun()
    ilerleme = c.setdefault("gorev_ilerleme", {}).setdefault(uid, {})
    if ilerleme.get(f"{tip_key}_gun", "") != bugun_key:
        ilerleme[f"{tip_key}_gun"] = bugun_key
        ilerleme[f"{tip_key}_sayi"] = 0
    ilerleme[f"{tip_key}_sayi"] = ilerleme.get(f"{tip_key}_sayi", 0) + artir
    return ilerleme[f"{tip_key}_sayi"]

def rozet_al(c, uid):
    """Kullanıcının güncel rozetini döner"""
    b = get_bakiye(c, uid)
    sev = hesapla_seviye(c, b.get("puan", 0))
    return ROZETLER.get(sev, "🌱")

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
    # Kullanıcıyı kaydet (DM listesi için)
    kaydet_kullanici(c, update.effective_user)
    if not c["adminler"]:
        c["adminler"].append(uid); save(c)
    if not is_admin(uid):
        # Üye /start yaptı - kaydet ve yardım göster
        b = get_bakiye(c, str(uid))
        sev = hesapla_seviye(c, b["puan"])
        bonus_alindi = c["gunluk_bonus_al"].get(str(uid),"") == bugun()
        bot_isim = c.get("marka_isim","Bot")
        await update.message.reply_text(
            f"<b>Merhaba! {update.effective_user.first_name}</b>\n\n"
            f"Seviye {sev} | {b['puan']:,} puan\n"
            f"{'✅ Bonus alindi' if bonus_alindi else f'/bonus yazarak {c[chr(34)+chr(103)+chr(117)+chr(110)+chr(108)+chr(117)+chr(107)+chr(95)+chr(98)+chr(111)+chr(110)+chr(117)+chr(115)+chr(34)]} puan kazan!'}\n\n"
            f"/yardim — Tum komutlar",
            parse_mode="HTML")
        save(c)
        return
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
        durum = "Acik" if c["casino_aktif"] else "Kapali"
        await q.edit_message_text(
            f"<b>Casino Modulu</b>\n\n"
            f"Durum: {durum}\n"
            f"Min bahis: {c['casino_min_bahis']} | Maks: {c['casino_max_bahis']:,} puan\n\n"
            "<b>18 Oyun:</b>\n"
            "/zar [bahis] | /tura [bahis] yazi|tura\n"
            "/slot [bahis] | /rulet [bahis] [tahmin]\n"
            "/balik [bahis] | /mines [bahis] [1-5]\n"
            "/tahmin [bahis] [1-10] | /kart [bahis]\n"
            "/ya [bahis] yuksek|alcak | /tombala [bahis]\n"
            "/savas [bahis] | /hediye [bahis]\n"
            "/bowling [bahis] | /dart [bahis]\n"
            "/basketbol [bahis] | /penalti [bahis] [yon]\n"
            "/btc /eth /ton — Kripto fiyat",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Ac/Kapat", callback_data="casino_toggle")],
                [InlineKeyboardButton("Min Bahis", callback_data="casino_min"),
                 InlineKeyboardButton("Maks Bahis", callback_data="casino_max")],
                [InlineKeyboardButton("Geri", callback_data="ana")],
            ]))
    elif d == "m_bakiye":
        top_puan = sum(v.get("puan",0) for v in c["bakiyeler"].values())
        vip_n = sum(1 for u2 in c["bakiyeler"] if is_vip(c,u2))
        str_max = max((c.get("streak_kayitlar",{}).get(u,{}).get("gun",0) for u in c["bakiyeler"]),default=0)
        durum = "Acik" if c["bakiye_aktif"] else "Kapali"
        await q.edit_message_text(
            f"<b>Bakiye ve Puan Sistemi</b>\n\n"
            f"Durum: {durum} | {len(c['bakiyeler'])} kisi | VIP: {vip_n}\n"
            f"Toplam puan: {top_puan:,} | En uzun seri: {str_max} gun\n\n"
            f"Gunluk bonus: {c['gunluk_bonus']} puan\n"
            f"Haftalik bonus: {c.get('haftalik_bonus',500)} puan\n"
            f"Seri katsayisi: +{c.get('streak_bonus_katsayi',20)}/gun (maks {c.get('streak_max',7)} gun)\n"
            f"Aktiflik: {c.get('aktiflik_puan',2)} puan/dk\n"
            f"Davet: {c['ref_odul']} puan/kisi\n"
            f"VIP esigi: {c.get('vip_esik',10000):,} puan (x{c.get('vip_bonus_katsayi',1.5)})\n"
            f"Puan carpani: {c.get('puan_carpan',1.0)}x",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Ac/Kapat", callback_data="bakiye_toggle")],
                [InlineKeyboardButton("Gunluk Bonus", callback_data="bakiye_bonus"),
                 InlineKeyboardButton("Haftalik Bonus", callback_data="bakiye_haftalik")],
                [InlineKeyboardButton("Seri Ayarla", callback_data="bakiye_streak"),
                 InlineKeyboardButton("Aktiflik Puani", callback_data="bakiye_aktiflik")],
                [InlineKeyboardButton("VIP Esigi", callback_data="bakiye_vip"),
                 InlineKeyboardButton("Puan Carpani", callback_data="bakiye_carpan")],
                [InlineKeyboardButton("Manuel Ver/Al", callback_data="bakiye_ver"),
                 InlineKeyboardButton("Liderlik Top10", callback_data="bakiye_top")],
                [InlineKeyboardButton("Seviye Tablosu", callback_data="bakiye_seviye_tablo"),
                 InlineKeyboardButton("Tumunu Sifirla", callback_data="bakiye_sifirla_onay")],
                [InlineKeyboardButton("Geri", callback_data="ana")],
            ]))
    elif d == "bakiye_toggle":
        c["bakiye_aktif"] = not c["bakiye_aktif"]; save(c); await cb(update,context)
    elif d == "bakiye_bonus":
        await q.edit_message_text(f"Gunluk Bonus\n\nSu an: {c['gunluk_bonus']} puan\nYeni miktar:", reply_markup=geri_kb("m_bakiye"))
        context.user_data["bekle"] = "gunluk_bonus"
    elif d == "bakiye_haftalik":
        await q.edit_message_text(f"Haftalik Bonus\n\nSu an: {c.get('haftalik_bonus',500)} puan\nYeni miktar:", reply_markup=geri_kb("m_bakiye"))
        context.user_data["bekle"] = "haftalik_bonus"
    elif d == "bakiye_streak":
        await q.edit_message_text(f"Seri Bonusu\n\nKatsayi: +{c.get('streak_bonus_katsayi',20)}/gun\nMaks: {c.get('streak_max',7)} gun\n\nYaz: [katsayi] [maks_gun]\nOrnek: 20 7", reply_markup=geri_kb("m_bakiye"))
        context.user_data["bekle"] = "streak_ayar"
    elif d == "bakiye_aktiflik":
        await q.edit_message_text(f"Aktiflik Puani\n\nSu an: {c.get('aktiflik_puan',2)} puan/dk\n0=kapali\nYeni miktar:", reply_markup=geri_kb("m_bakiye"))
        context.user_data["bekle"] = "aktiflik_puan"
    elif d == "bakiye_vip":
        await q.edit_message_text(f"VIP Sistemi\n\nEsik: {c.get('vip_esik',10000):,} puan\nBonus: x{c.get('vip_bonus_katsayi',1.5)}\n\nYaz: [esik] [katsayi]\nOrnek: 10000 1.5", reply_markup=geri_kb("m_bakiye"))
        context.user_data["bekle"] = "vip_ayar"
    elif d == "bakiye_carpan":
        await q.edit_message_text(f"Puan Carpani\n\nSu an: {c.get('puan_carpan',1.0)}x\n1.0=normal, 2.0=cift puan", reply_markup=geri_kb("m_bakiye"))
        context.user_data["bekle"] = "puan_carpan"
    elif d == "bakiye_ver":
        await q.edit_message_text("Manuel Ver/Al\n\n[user_id] [miktar]\nNegatif=al\nOrnek: 123456789 500", reply_markup=geri_kb("m_bakiye"))
        context.user_data["bekle"] = "bakiye_ver"
    elif d == "bakiye_top":
        sirali = sorted(c["bakiyeler"].items(),key=lambda x:x[1].get("puan",0),reverse=True)[:10]
        rows = [f"{i+1}. Sev{hesapla_seviye(c,v.get(chr(112)+chr(117)+chr(97)+chr(110),0))} {v.get('isim','?')}: {v.get('puan',0):,}" for i,(u2,v) in enumerate(sirali)]
        await q.edit_message_text(f"<b>Top10</b>\n\n{chr(10).join(rows) or 'Bos.'}", parse_mode="HTML", reply_markup=geri_kb("m_bakiye"))
    elif d == "bakiye_seviye_tablo":
        e = c.get("seviye_esikleri",{})
        txt = "\n".join([f"Seviye {s}: {int(esik):,} puan" for s,esik in sorted(e.items(),key=lambda x:int(x[0]))])
        await q.edit_message_text(f"<b>Seviye Tablosu</b>\n\n{txt}", parse_mode="HTML", reply_markup=geri_kb("m_bakiye"))
    elif d == "bakiye_sifirla_onay":
        await q.edit_message_text("Tum bakiyeler silinecek. Emin misin?",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Evet",callback_data="bakiye_sifirla"),InlineKeyboardButton("Iptal",callback_data="m_bakiye")]]))
    elif d == "bakiye_sifirla":
        c["bakiyeler"]={};c["streak_kayitlar"]={};c["gunluk_bonus_al"]={};c.setdefault("haftalik_bonus_al",{}).clear()
        save(c); await q.answer("Sifirlandı!",show_alert=True); await cb(update,context)

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
    c = cfg()
    if not c["bakiye_aktif"]: return
    uid = str(update.effective_user.id)
    b = get_bakiye(c, uid)
    sev = hesapla_seviye(c, b["puan"])
    son_puan, son_sev = sonraki_seviye(c, b["puan"])
    streak = c.get("streak_kayitlar",{}).get(uid,{}).get("gun",0)
    vip_tag = " [VIP]" if is_vip(c, uid) else ""
    ref_n = len(c.get("ref_kayitlar",{}).get(uid,[]))
    if son_puan:
        sev_esik = int(c.get("seviye_esikleri",{}).get(str(sev),0))
        dolu = int((b["puan"]-sev_esik) / max(1,son_puan-sev_esik) * 10)
        kalan = son_puan - b["puan"]
        bar = chr(9608)*dolu + chr(9617)*(10-dolu) + f" Sev.{son_sev} ({kalan:,} kaldi)"
    else:
        bar = "MAKSIMUM SEVIYE"
    bonus_alindi = c["gunluk_bonus_al"].get(uid,"") == bugun()
    await update.message.reply_text(
        f"<b>Bakiye Kart{vip_tag}</b>\n\n"
        f"Seviye {sev} | {b['puan']:,} puan\n"
        f"{bar}\n\n"
        f"Toplam kazanilan: {b.get('toplam',0):,}\n"
        f"Giris serisi: {streak} gun\n"
        f"Davet: {ref_n} kisi\n"
        f"Gunluk bonus: {'Alindi' if bonus_alindi else f'/bonus -> +{c[chr(34)+chr(103)+chr(117)+chr(110)+chr(108)+chr(117)+chr(107)+chr(95)+chr(98)+chr(111)+chr(110)+chr(117)+chr(115)+chr(34)]} puan'}\n\n"
        f"/gorev /market /top /hbonus /seviye",
        parse_mode="HTML")

async def bonus_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = cfg()
    if not c["bakiye_aktif"]: return
    uid = str(update.effective_user.id); isim = update.effective_user.first_name
    if c["gunluk_bonus_al"].get(uid,"") == bugun():
        streak = c.get("streak_kayitlar",{}).get(uid,{}).get("gun",0)
        return await update.message.reply_text(f"Bugun bonusunu aldin.\nSerin: {streak} gun. Yarin tekrar gel!")
    if "streak_kayitlar" not in c: c["streak_kayitlar"] = {}
    sd = c["streak_kayitlar"].get(uid, {"gun":0,"son":""})
    dun = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    sd["gun"] = min(sd["gun"]+1, c.get("streak_max",7)) if sd.get("son")==dun else 1
    sd["son"] = bugun()
    c["streak_kayitlar"][uid] = sd
    gun = sd["gun"]
    temel = c["gunluk_bonus"]
    ekstra = int((gun-1) * c.get("streak_bonus_katsayi",20))
    toplam_b = temel + ekstra
    yeni = add_puan(c, uid, isim, toplam_b)
    c["gunluk_bonus_al"][uid] = bugun(); save(c)
    sev = hesapla_seviye(c, yeni)
    streak_bar = "F"*gun + "."*(c.get("streak_max",7)-gun)
    msg = f"Gunluk Bonus!\nTemel: +{temel}"
    if ekstra > 0: msg += f" | Seri ({gun}. gun): +{ekstra}"
    msg += f"\nToplam: +{toplam_b} puan\n[{streak_bar}] {gun}. gun\nSeviye {sev} | {yeni:,} puan"
    # Görev tetikle
    gorev_tamamla(c, uid, isim, "ilk_giris")  # Tek seferlik
    gorev_tamamla(c, uid, isim, "gunluk_bonus")  # Günlük
    if gun >= 7: gorev_tamamla(c, uid, isim, "haftalik_seri")  # Haftalık
    # Seviye görevleri
    if sev >= 5: gorev_tamamla(c, uid, isim, "sev5")
    if sev >= 10: gorev_tamamla(c, uid, isim, "sev10")
    if is_vip(c, uid): gorev_tamamla(c, uid, isim, "vip_ol")
    save(c)
    await update.message.reply_text(msg)

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
    c = cfg()
    uid = str(update.effective_user.id)
    sirali = sorted(c["bakiyeler"].items(),key=lambda x:x[1].get("puan",0),reverse=True)
    md = ["1.","2.","3."]
    rows = []
    for i,(uid2,v) in enumerate(sirali[:10]):
        sev = hesapla_seviye(c,v.get("puan",0))
        vtag = "[VIP]" if is_vip(c,uid2) else ""
        rows.append(f"{md[i] if i<3 else str(i+1)+'.'} {vtag}Sev{sev} {v.get('isim','?')}: {v.get('puan',0):,} puan")
    kendi = next((i+1 for i,(u,_) in enumerate(sirali) if u==uid),None)
    kendi_p = c["bakiyeler"].get(uid,{}).get("puan",0)
    alt = f"\nSenin siran: {kendi}. | {kendi_p:,} puan" if kendi and kendi>10 else ""
    await update.message.reply_text(
        f"<b>Liderlik Tablosu</b>\n\n"
        + "\n".join(rows or ["Henuz kimse yok."]) + alt
        + f"\n\n{len(c['bakiyeler'])} kisi kayitli",
        parse_mode="HTML")

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
        hata, bahis = bahis_kontrol(c, uid, context.args[0])
        if hata: return await update.message.reply_text(hata)
        b = get_bakiye(c, uid)
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
        hata, bahis = bahis_kontrol(c, uid, context.args[0])
        if hata: return await update.message.reply_text(hata)
        tahmin=context.args[1].lower() if len(context.args)>1 else "yazı"
        b = get_bakiye(c, uid)
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
        hata, bahis = bahis_kontrol(c, uid, context.args[0])
        if hata: return await update.message.reply_text(hata)
        b = get_bakiye(c, uid)
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
        hata, bahis = bahis_kontrol(c, uid, context.args[0])
        if hata: return await update.message.reply_text(hata)
        tahmin=" ".join(context.args[1:]).lower()
        b = get_bakiye(c, uid)
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
        try: c["ref_odul"]=int(metin); save(c); context.user_data["bekle"]=None; await update.message.reply_text(f"Odül: {metin} puan", reply_markup=ana_kb())
        except: await update.message.reply_text("Sayi gir.")
    elif bekle=="haftalik_bonus":
        try: c["haftalik_bonus"]=int(metin); save(c); context.user_data["bekle"]=None; await update.message.reply_text(f"Haftalik: {metin} puan", reply_markup=ana_kb())
        except: await update.message.reply_text("Sayi gir.")
    elif bekle=="streak_ayar":
        try:
            p=metin.strip().split(); c["streak_bonus_katsayi"]=int(p[0]); c["streak_max"]=int(p[1]); save(c)
            context.user_data["bekle"]=None; await update.message.reply_text(f"Seri: +{p[0]}/gun, maks {p[1]} gun", reply_markup=ana_kb())
        except: await update.message.reply_text("Format: 20 7")
    elif bekle=="aktiflik_puan":
        try: c["aktiflik_puan"]=int(metin); save(c); context.user_data["bekle"]=None; await update.message.reply_text(f"Aktiflik: {metin} puan/dk", reply_markup=ana_kb())
        except: await update.message.reply_text("Sayi gir (0=kapali)")
    elif bekle=="vip_ayar":
        try:
            p=metin.strip().split(); c["vip_esik"]=int(p[0]); c["vip_bonus_katsayi"]=float(p[1]); save(c)
            context.user_data["bekle"]=None; await update.message.reply_text(f"VIP: {int(p[0]):,} puan, x{float(p[1])}", reply_markup=ana_kb())
        except: await update.message.reply_text("Format: 10000 1.5")
    elif bekle=="puan_carpan":
        try: c["puan_carpan"]=float(metin); save(c); context.user_data["bekle"]=None; await update.message.reply_text(f"Carpan: {metin}x", reply_markup=ana_kb())
        except: await update.message.reply_text("Sayi gir (orn: 2.0)")
    elif bekle=="bakiye_ver":
        try:
            p=metin.strip().split(); uid2,miktar=p[0],int(p[1])
            yeni=add_puan(c,uid2,f"Kullanici {uid2}",miktar)
            context.user_data["bekle"]=None; await update.message.reply_text(f"Tamam: {uid2} -> {miktar:+,} | Toplam: {yeni:,}", reply_markup=ana_kb())
        except: await update.message.reply_text("Format: [user_id] [miktar]")
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

# ═══════════════════════════════════════════════════════════════
#  YENİ OYUNLAR + ADMİN YETKİ SİSTEMİ — v5.1 EK MODÜL
# ═══════════════════════════════════════════════════════════════

# ── ADMİN YETKİ SİSTEMİ ────────────────────────────────────────
# Yetki seviyeleri:
# 3 = Süper Admin (her şey)
# 2 = Moderatör (warn/ban/kick/mute + casino yönet)
# 1 = Yardımcı (sadece warn + mesaj silme)

async def mines_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """💣 Mayın Tarlası — 9 kutucuk, mayına basma!"""
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if not context.args:
        return await update.message.reply_text(
            "💣 <b>Mayın Tarlası</b>\n\nKullanım: /mines [bahis] [mayın_sayısı 1-5]\n"
            "Örnek: /mines 100 3\n\nDaha fazla mayın = daha yüksek ödül!", parse_mode="HTML")
    try:
        bahis = int(context.args[0])
        mayin_sayi = int(context.args[1]) if len(context.args) > 1 else 3
        mayin_sayi = max(1, min(5, mayin_sayi))
        b = get_bakiye(c, uid)
        if b["puan"] < bahis: return await update.message.reply_text("❌ Yetersiz bakiye!")
        if bahis < c["casino_min_bahis"] or bahis > c["casino_max_bahis"]:
            return await update.message.reply_text(f"❌ Bahis {c['casino_min_bahis']}-{c['casino_max_bahis']} arası!")

        # 9 kutucuk, mayın_sayi adet mayın
        kutucuklar = ["💣"] * mayin_sayi + ["💎"] * (9 - mayin_sayi)
        random.shuffle(kutucuklar)
        secilen = random.randint(0, 8)

        if kutucuklar[secilen] == "💣":
            kazanc = -bahis
            sonuc_txt = "💥 <b>PATLADI!</b> Mayına bastın!"
        else:
            carpan = round(1 + (mayin_sayi * 0.5), 1)
            kazanc = int(bahis * carpan) - bahis
            sonuc_txt = f"💎 <b>GÜVENLİ!</b> {carpan}x çarpan!"

        # Tahtayı göster
        tahta = ""
        for i, k in enumerate(kutucuklar):
            if i == secilen: tahta += f"[{k}]"
            else: tahta += "[ ]" if kutucuklar[i] == "💎" else "[💣]" if kazanc < 0 else "[ ]"
            if (i + 1) % 3 == 0: tahta += "\n"

        yeni = add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"] += 1; save(c)
        await update.message.reply_text(
            f"💣 <b>Mayın Tarlası</b> ({mayin_sayi} mayın)\n\n{tahta}\n"
            f"{sonuc_txt}\n{'➕' if kazanc > 0 else '➖'} <b>{abs(kazanc):,} puan</b>\n"
            f"💰 Bakiye: <b>{yeni:,}</b>", parse_mode="HTML")
    except: await update.message.reply_text("❌ Kullanım: /mines [bahis] [1-5 mayın]")


async def balik_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🎣 Balık Avı — Şans oyunu, farklı balıklar farklı ödüller"""
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if not context.args:
        return await update.message.reply_text("Kullanim: /balik [bahis]")
    try:
        hata, bahis = bahis_kontrol(c, uid, context.args[0])
        if hata: return await update.message.reply_text(hata)
        b = get_bakiye(c, uid)

        baliklar = [
            ("🦈 KÖPEK BALIĞI",  5,  0.03),
            ("🐋 BALİNA",        4,  0.05),
            ("🐠 TROPIKAL BALIK",3,  0.12),
            ("🐟 NORMAL BALIK",  1.5,0.30),
            ("🦐 KARİDES",       0.5,0.25),
            ("👢 ESKİ BOT",     -1,  0.15),
            ("🌿 YOSUN",        -0.5,0.10),
        ]
        r = random.random(); toplam = 0
        secilen = baliklar[-1]
        for balik, carpan, oran in baliklar:
            toplam += oran
            if r <= toplam:
                secilen = (balik, carpan, oran); break

        balik_isim, carpan, _ = secilen
        if carpan > 0: kazanc = int(bahis * carpan) - bahis
        else: kazanc = int(bahis * abs(carpan)) * -1

        yeni = add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"] += 1; save(c)
        await update.message.reply_text(
            f"🎣 <b>Balık Avı</b>\n\n🌊 Olta attın...\n\n{balik_isim}!\n\n"
            f"{'➕' if kazanc >= 0 else '➖'} <b>{abs(kazanc):,} puan</b>\n"
            f"💰 Bakiye: <b>{yeni:,}</b>", parse_mode="HTML")
    except: await update.message.reply_text("❌ Kullanım: /balik [bahis]")


async def tahmin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🔢 Sayı Tahmin — 1-10 arası sayı tah, 8x ödül!"""
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if len(context.args) < 2:
        return await update.message.reply_text("🔢 Kullanım: /tahmin [bahis] [1-10]\nDoğru tahmin = 8x ödül!")
    try:
        bahis = int(context.args[0]); tahmin = int(context.args[1])
        if not 1 <= tahmin <= 10: return await update.message.reply_text("❌ 1-10 arası bir sayı gir!")
        b = get_bakiye(c, uid)
        if b["puan"] < bahis: return await update.message.reply_text("❌ Yetersiz bakiye!")
        if bahis < c["casino_min_bahis"] or bahis > c["casino_max_bahis"]:
            return await update.message.reply_text(f"❌ Bahis {c['casino_min_bahis']}-{c['casino_max_bahis']} arası!")

        sayi = random.randint(1, 10)
        if tahmin == sayi:
            kazanc = bahis * 8; txt = "🎯 TAM İSABET! 8x!"
        elif abs(tahmin - sayi) == 1:
            kazanc = int(bahis * 0.5); txt = "🎉 Yakın! 0.5x bonus!"
        else:
            kazanc = -bahis; txt = "😢 Yanlış tahmin!"

        yeni = add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"] += 1; save(c)
        await update.message.reply_text(
            f"🔢 <b>Sayı Tahmin</b>\n\nTahmin: {tahmin}  |  Gerçek: <b>{sayi}</b>\n\n"
            f"{txt}\n{'➕' if kazanc > 0 else '➖'} <b>{abs(kazanc):,} puan</b>\n"
            f"💰 Bakiye: <b>{yeni:,}</b>", parse_mode="HTML")
    except: await update.message.reply_text("❌ Kullanım: /tahmin [bahis] [1-10]")


async def kart_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🃏 Kart Oyunu — Yüksek kart kazanır (Blackjack benzeri)"""
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if not context.args:
        return await update.message.reply_text("🃏 Kullanım: /kart [bahis]\nSenin kartın botunkinden yüksekse 2x kazanırsın!")
    try:
        bahis = int(context.args[0]); b = get_bakiye(c, uid)
        if b["puan"] < bahis: return await update.message.reply_text("❌ Yetersiz bakiye!")
        if bahis < c["casino_min_bahis"] or bahis > c["casino_max_bahis"]:
            return await update.message.reply_text(f"❌ Bahis {c['casino_min_bahis']}-{c['casino_max_bahis']} arası!")

        kartlar = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
        degerler = {str(i): i for i in range(2,11)}; degerler.update({"J":11,"Q":12,"K":13,"A":14})
        ogeler = ["♠️","♥️","♦️","♣️"]

        oyuncu_kart = random.choice(kartlar)
        bot_kart = random.choice(kartlar)
        oyuncu_renk = random.choice(ogeler)
        bot_renk = random.choice(ogeler)

        oy_d = degerler[oyuncu_kart]; bot_d = degerler[bot_kart]

        if oy_d > bot_d: kazanc = bahis; txt = "🎉 Kazandın! Kartın daha yüksek!"
        elif oy_d < bot_d: kazanc = -bahis; txt = "😢 Kaybettin! Botun kartı daha yüksek!"
        else: kazanc = 0; txt = "🤝 Beraberlik! Bahis iade edildi."

        yeni = add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"] += 1; save(c)
        await update.message.reply_text(
            f"🃏 <b>Kart Oyunu</b>\n\n"
            f"Sen: <b>{oyuncu_kart}{oyuncu_renk}</b>  vs  Bot: <b>{bot_kart}{bot_renk}</b>\n\n"
            f"{txt}\n{'➕' if kazanc > 0 else '➖' if kazanc < 0 else '🔄'} <b>{abs(kazanc):,} puan</b>\n"
            f"💰 Bakiye: <b>{yeni:,}</b>", parse_mode="HTML")
    except: await update.message.reply_text("❌ Kullanım: /kart [bahis]")


async def yuksek_alcak_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📊 Yüksek/Alçak — Sonraki kart yüksek mi alçak mı?"""
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if len(context.args) < 2:
        return await update.message.reply_text("📊 Kullanım: /ya [bahis] yüksek|alçak\n1.8x ödül!")
    try:
        bahis = int(context.args[0]); tahmin = context.args[1].lower()
        if tahmin not in ["yüksek","yuksek","alçak","alcak"]:
            return await update.message.reply_text("❌ yüksek veya alçak yaz!")
        b = get_bakiye(c, uid)
        if b["puan"] < bahis: return await update.message.reply_text("❌ Yetersiz bakiye!")
        if bahis < c["casino_min_bahis"] or bahis > c["casino_max_bahis"]:
            return await update.message.reply_text(f"❌ Bahis {c['casino_min_bahis']}-{c['casino_max_bahis']} arası!")

        mevcut = random.randint(1, 13)
        sonraki = random.randint(1, 13)
        kartlar = {1:"A",11:"J",12:"Q",13:"K"}

        def kart_isim(n): return kartlar.get(n, str(n))

        dogru_tahmin = (sonraki > mevcut and tahmin in ["yüksek","yuksek"]) or \
                       (sonraki < mevcut and tahmin in ["alçak","alcak"]) or \
                       (sonraki == mevcut)

        if dogru_tahmin: kazanc = int(bahis * 0.8); txt = "✅ Doğru tahmin! 1.8x"
        else: kazanc = -bahis; txt = "❌ Yanlış tahmin!"

        yeni = add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"] += 1; save(c)
        await update.message.reply_text(
            f"📊 <b>Yüksek / Alçak</b>\n\n"
            f"Mevcut: <b>{kart_isim(mevcut)}</b> → Sonraki: <b>{kart_isim(sonraki)}</b>\n"
            f"Tahmin: {tahmin}\n\n{txt}\n"
            f"{'➕' if kazanc > 0 else '➖'} <b>{abs(kazanc):,} puan</b>\n"
            f"💰 Bakiye: <b>{yeni:,}</b>", parse_mode="HTML")
    except: await update.message.reply_text("❌ Kullanım: /ya [bahis] yüksek")


async def tombala_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🎱 Tombala — 5 sayı çek, 3 veya daha fazlası tutarsa kazan!"""
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if not context.args:
        return await update.message.reply_text("🎱 Kullanım: /tombala [bahis]\n3 eşleşme=1.5x | 4=3x | 5=10x!")
    try:
        bahis = int(context.args[0]); b = get_bakiye(c, uid)
        if b["puan"] < bahis: return await update.message.reply_text("❌ Yetersiz bakiye!")
        if bahis < c["casino_min_bahis"] or bahis > c["casino_max_bahis"]:
            return await update.message.reply_text(f"❌ Bahis {c['casino_min_bahis']}-{c['casino_max_bahis']} arası!")

        oyuncu_sayilari = random.sample(range(1, 26), 5)
        cekilen_sayilar = random.sample(range(1, 26), 10)
        eslesen = [s for s in oyuncu_sayilari if s in cekilen_sayilar]
        eslesme = len(eslesen)

        if eslesme >= 5: kazanc = bahis * 10; txt = "🎊 TOMBALA! 10x!"
        elif eslesme == 4: kazanc = bahis * 3; txt = "🎉 4 Eşleşme! 3x!"
        elif eslesme == 3: kazanc = int(bahis * 0.5); txt = "✨ 3 Eşleşme! 1.5x!"
        else: kazanc = -bahis; txt = f"😢 Sadece {eslesme} eşleşme, kaybettin!"

        oyuncu_txt = " ".join([f"{'✅' if s in eslesen else '❌'}{s}" for s in oyuncu_sayilari])
        yeni = add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"] += 1; save(c)
        await update.message.reply_text(
            f"🎱 <b>Tombala</b>\n\n"
            f"Sayıların: {oyuncu_txt}\n"
            f"Çekilen: {' '.join(map(str,cekilen_sayilar[:8]))}...\n\n"
            f"{txt}\n{'➕' if kazanc > 0 else '➖'} <b>{abs(kazanc):,} puan</b>\n"
            f"💰 Bakiye: <b>{yeni:,}</b>", parse_mode="HTML")
    except: await update.message.reply_text("❌ Kullanım: /tombala [bahis]")


async def savas_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """⚔️ Savaş — Başka bir kullanıcıyla puan savaşı"""
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚔️ Savaşmak için bir mesajı yanıtla!\n/savas [bahis]")
    if not context.args:
        return await update.message.reply_text("Kullanım: /savas [bahis] (birinin mesajını yanıtlayarak)")
    try:
        bahis = int(context.args[0])
        rakip = update.message.reply_to_message.from_user
        if rakip.id == update.effective_user.id:
            return await update.message.reply_text("❌ Kendinle savaşamazsın!")
        if rakip.is_bot:
            return await update.message.reply_text("❌ Bot ile savaşamazsın!")

        b1 = get_bakiye(c, uid)
        b2 = get_bakiye(c, str(rakip.id))
        if b1["puan"] < bahis: return await update.message.reply_text("❌ Yetersiz bakiyen!")
        if b2["puan"] < bahis: return await update.message.reply_text(f"❌ {rakip.first_name}'in bakiyesi yetersiz!")
        if bahis < c["casino_min_bahis"] or bahis > c["casino_max_bahis"]:
            return await update.message.reply_text(f"❌ Bahis {c['casino_min_bahis']}-{c['casino_max_bahis']} arası!")

        # Savaş simülasyonu
        oyuncu_hp = 100; rakip_hp = 100
        turlar = []
        for _ in range(5):
            oyuncu_hasar = random.randint(10, 35)
            rakip_hasar  = random.randint(10, 35)
            rakip_hp  -= oyuncu_hasar
            oyuncu_hp -= rakip_hasar
            turlar.append(f"⚔️ Sen -{rakip_hasar} HP  |  {rakip.first_name} -{oyuncu_hasar} HP")
            if oyuncu_hp <= 0 or rakip_hp <= 0: break

        if oyuncu_hp > rakip_hp:
            add_puan(c, uid, isim, bahis)
            add_puan(c, str(rakip.id), rakip.first_name, -bahis)
            kazanan_txt = f"🏆 <b>{isim} KAZANDI!</b>"
        elif rakip_hp > oyuncu_hp:
            add_puan(c, uid, isim, -bahis)
            add_puan(c, str(rakip.id), rakip.first_name, bahis)
            kazanan_txt = f"🏆 <b>{rakip.first_name} KAZANDI!</b>"
        else:
            kazanan_txt = "🤝 <b>BERABERLIK!</b>"

        c["stats"]["casino_oyun"] += 1; save(c)
        tur_txt = "\n".join(turlar[-3:])
        await update.message.reply_text(
            f"⚔️ <b>{isim} vs {rakip.first_name}</b>\n\n"
            f"{tur_txt}\n\n"
            f"❤️ {isim}: {max(0,oyuncu_hp)} HP\n"
            f"❤️ {rakip.first_name}: {max(0,rakip_hp)} HP\n\n"
            f"{kazanan_txt}\n💰 Bahis: {bahis:,} puan", parse_mode="HTML")
    except Exception as e: await update.message.reply_text(f"❌ Hata: {e}")


async def hediye_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🎁 Hediye Kutusu — Rastgele ödül veya ceza"""
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if not context.args:
        return await update.message.reply_text("🎁 Kullanım: /hediye [bahis]\nKutuyu aç, ne çıkacak bilinmez!")
    try:
        bahis = int(context.args[0]); b = get_bakiye(c, uid)
        if b["puan"] < bahis: return await update.message.reply_text("❌ Yetersiz bakiye!")

        hediyeler = [
            ("💎 Elmas Kutu", 5,   0.02),
            ("🥇 Altın Kutu", 3,   0.08),
            ("🥈 Gümüş Kutu", 1.5, 0.20),
            ("📦 Normal Kutu",0.5, 0.35),
            ("💩 Boş Kutu",  -0.5, 0.25),
            ("💣 Bomba",     -2,   0.10),
        ]
        r = random.random(); toplam = 0
        secilen = hediyeler[-1]
        for h in hediyeler:
            toplam += h[2]
            if r <= toplam: secilen = h; break

        isim_h, carpan, _ = secilen
        kazanc = int(bahis * carpan) if carpan > 0 else int(bahis * abs(carpan)) * -1
        yeni = add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"] += 1; save(c)
        await update.message.reply_text(
            f"🎁 <b>Hediye Kutusu</b>\n\n🎊 Kutuyu açtın...\n\n{isim_h}!\n\n"
            f"{'➕' if kazanc >= 0 else '➖'} <b>{abs(kazanc):,} puan</b>\n"
            f"💰 Bakiye: <b>{yeni:,}</b>", parse_mode="HTML")
    except: await update.message.reply_text("❌ Kullanım: /hediye [bahis]")


# ── ADMİN YETKİ CALLBACK EKLEMELERİ ───────────────────────────
_orijinal_cb = cb

async def bowling_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🎳 Bowling — 10 pin, kaç tanesini devirebilirsin?"""
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if not context.args:
        return await update.message.reply_text(
            "🎳 Kullanım: /bowling [bahis]\n\nStrike(10)=3x | Spare(9)=1.5x | 7-8=1x | <7=kayıp")
    try:
        bahis = int(context.args[0]); b = get_bakiye(c, uid)
        if b["puan"] < bahis: return await update.message.reply_text("❌ Yetersiz bakiye!")
        if bahis < c["casino_min_bahis"] or bahis > c["casino_max_bahis"]:
            return await update.message.reply_text(f"❌ {c['casino_min_bahis']}-{c['casino_max_bahis']} arası!")

        atış1 = random.randint(0, 10)
        atış2 = random.randint(0, 10 - atış1) if atış1 < 10 else 0
        toplam = atış1 + atış2

        pin_emoji = lambda n: "🎳" * n + "⬜" * (10 - n)

        if atış1 == 10:
            kazanc = bahis * 3; txt = "🏆 STRİKE! 3x! Tüm pinler devrildi!"
            gosterim = f"1. atış: {pin_emoji(10)}\n✨ STRİKE!"
        elif toplam == 10:
            kazanc = int(bahis * 1.5); txt = "✅ SPARE! 1.5x! İki atışta temizledin!"
            gosterim = f"1. atış: {pin_emoji(atış1)}\n2. atış: {pin_emoji(atış2)}\n✨ SPARE!"
        elif toplam >= 7:
            kazanc = 0; txt = f"😊 {toplam} pin! Beraberlik, bahis iade."
            gosterim = f"1. atış: {pin_emoji(atış1)}\n2. atış: {pin_emoji(atış2)}"
        else:
            kazanc = -bahis; txt = f"😢 Sadece {toplam} pin devrildi!"
            gosterim = f"1. atış: {pin_emoji(atış1)}\n2. atış: {pin_emoji(atış2)}"

        yeni = add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"] += 1; save(c)
        await update.message.reply_text(
            f"🎳 <b>Bowling</b>\n\n{gosterim}\n\n{txt}\n"
            f"{'➕' if kazanc > 0 else '➖' if kazanc < 0 else '🔄'} <b>{abs(kazanc):,} puan</b>\n"
            f"💰 Bakiye: <b>{yeni:,}</b>", parse_mode="HTML")
    except: await update.message.reply_text("❌ Kullanım: /bowling [bahis]")


# ── DART ────────────────────────────────────────────────────────
async def dart_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🎯 Dart — Hedef tahtasına at, bullseye = 5x!"""
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if not context.args:
        return await update.message.reply_text(
            "🎯 Kullanım: /dart [bahis]\n\n🎯 Bullseye=5x | 🟡 İç=2x | 🔵 Orta=1x | ⚪ Dış=kayıp")
    try:
        bahis = int(context.args[0]); b = get_bakiye(c, uid)
        if b["puan"] < bahis: return await update.message.reply_text("❌ Yetersiz bakiye!")
        if bahis < c["casino_min_bahis"] or bahis > c["casino_max_bahis"]:
            return await update.message.reply_text(f"❌ {c['casino_min_bahis']}-{c['casino_max_bahis']} arası!")

        sayi = random.random()
        if sayi < 0.05:
            bolge = "🎯 BULLSEYE"; carpan = 5; txt = "MÜKEMMEL ATIŞ! 5x!"
        elif sayi < 0.20:
            bolge = "🟡 İç Halka"; carpan = 2; txt = "Harika atış! 2x!"
        elif sayi < 0.50:
            bolge = "🔵 Orta Halka"; carpan = 1; txt = "İyi atış! 1x!"
        elif sayi < 0.75:
            bolge = "🔴 Dış Halka"; carpan = 0.5; txt = "Kenara yakın, 0.5x."
        else:
            bolge = "⚪ Kaçtı"; carpan = -1; txt = "Tamamen kaçtı! 😢"

        kazanc = int(bahis * carpan) if carpan > 0 else -bahis
        yeni = add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"] += 1; save(c)

        tahta = (
            "⚪⚪⚪⚪⚪\n"
            "⚪🔴🔴🔴⚪\n"
            "⚪🔴🔵🔴⚪\n"
            "⚪🔴🔴🔴⚪\n"
            "⚪⚪⚪⚪⚪"
        ) if carpan != 5 else (
            "⚪⚪⚪⚪⚪\n"
            "⚪🔴🔴🔴⚪\n"
            "⚪🔴🎯🔴⚪\n"
            "⚪🔴🔴🔴⚪\n"
            "⚪⚪⚪⚪⚪"
        )

        await update.message.reply_text(
            f"🎯 <b>Dart</b>\n\n{tahta}\n\n{bolge}\n{txt}\n"
            f"{'➕' if kazanc > 0 else '➖'} <b>{abs(kazanc):,} puan</b>\n"
            f"💰 Bakiye: <b>{yeni:,}</b>", parse_mode="HTML")
    except: await update.message.reply_text("❌ Kullanım: /dart [bahis]")


# ── BASKETBOL ───────────────────────────────────────────────────
async def basketbol_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🏀 Basketbol — Serbest atış, kaç sayı atarsın?"""
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if not context.args:
        return await update.message.reply_text("🏀 Kullanım: /basketbol [bahis]\n5 atış yaparsın, her sayı puan kazandırır!")
    try:
        bahis = int(context.args[0]); b = get_bakiye(c, uid)
        if b["puan"] < bahis: return await update.message.reply_text("❌ Yetersiz bakiye!")
        if bahis < c["casino_min_bahis"] or bahis > c["casino_max_bahis"]:
            return await update.message.reply_text(f"❌ {c['casino_min_bahis']}-{c['casino_max_bahis']} arası!")

        atislar = []
        isabet = 0
        for _ in range(5):
            r = random.random()
            if r < 0.15:
                atislar.append("🏀✨ 3 Sayı!"); isabet += 3
            elif r < 0.55:
                atislar.append("🏀 2 Sayı!"); isabet += 2
            elif r < 0.75:
                atislar.append("🏀 1 Sayı"); isabet += 1
            else:
                atislar.append("❌ Kaçtı"); pass

        if isabet >= 12: carpan = 4; txt = "🏆 Efsane oyun! 4x!"
        elif isabet >= 9: carpan = 2; txt = "🎉 Harika! 2x!"
        elif isabet >= 6: carpan = 1; txt = "👍 İyi oyun! 1x"
        elif isabet >= 3: carpan = 0; txt = "😊 Fena değil. Beraberlik."
        else: carpan = -1; txt = "😢 Kötü gün..."

        kazanc = int(bahis * carpan) if carpan > 0 else (-bahis if carpan < 0 else 0)
        yeni = add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"] += 1; save(c)
        await update.message.reply_text(
            f"🏀 <b>Basketbol</b>\n\n"
            + "\n".join(atislar) +
            f"\n\n🔢 Toplam: <b>{isabet} sayı</b>\n{txt}\n"
            f"{'➕' if kazanc > 0 else '➖' if kazanc < 0 else '🔄'} <b>{abs(kazanc):,} puan</b>\n"
            f"💰 Bakiye: <b>{yeni:,}</b>", parse_mode="HTML")
    except: await update.message.reply_text("❌ Kullanım: /basketbol [bahis]")


# ── FUTBOL ──────────────────────────────────────────────────────
async def futbol_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """⚽ Penaltı atışı — Kaleciye karşı şans dene!"""
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if len(context.args) < 2:
        return await update.message.reply_text(
            "⚽ Kullanım: /penalti [bahis] [sol|orta|sag]\nKaleci rastgele bir tarafa atlayacak!")
    try:
        bahis = int(context.args[0]); yon = context.args[1].lower()
        if yon not in ["sol","orta","sag","sağ"]:
            return await update.message.reply_text("❌ sol, orta veya sag yaz!")
        b = get_bakiye(c, uid)
        if b["puan"] < bahis: return await update.message.reply_text("❌ Yetersiz bakiye!")
        if bahis < c["casino_min_bahis"] or bahis > c["casino_max_bahis"]:
            return await update.message.reply_text(f"❌ {c['casino_min_bahis']}-{c['casino_max_bahis']} arası!")

        kaleci_yon = random.choice(["sol", "orta", "sag"])
        yon_emoji = {"sol":"⬅️","orta":"⬆️","sag":"➡️"}

        if yon in ["sag","sağ"]: yon = "sag"

        if yon != kaleci_yon:
            kazanc = int(bahis * 1.5); txt = "⚽ GOL! 1.5x!"
            kale = "┌─────────┐\n│    ⚽    │\n└─────────┘"
        else:
            kazanc = -bahis; txt = "🧤 Kaleci kurtardı!"
            kale = f"┌─────────┐\n│ 🧤{yon_emoji[kaleci_yon]}  │\n└─────────┘"

        yeni = add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"] += 1; save(c)
        await update.message.reply_text(
            f"⚽ <b>Penaltı Atışı</b>\n\n{kale}\n\n"
            f"Sen: {yon_emoji.get(yon,'?')}  Kaleci: {yon_emoji[kaleci_yon]}\n\n{txt}\n"
            f"{'➕' if kazanc > 0 else '➖'} <b>{abs(kazanc):,} puan</b>\n"
            f"💰 Bakiye: <b>{yeni:,}</b>", parse_mode="HTML")
    except: await update.message.reply_text("❌ Kullanım: /penalti [bahis] sol|orta|sag")


# ── PUAN KAZANMA SİSTEMİ ────────────────────────────────────────
# Üyeler şu yollarla puan kazanır:
# 1. /bonus — Günlük ücretsiz puan
# 2. /ref   — Davet sistemi
# 3. Mesaj yazmak — Aktiflik puanı
# 4. /gorev — Görev sistemi
# 5. Admin'den manuel /ver komutu
# 6. Etkinlik kazanma

# ── GÖREV TİPLERİ: "hic"=tek seferlik, "gun"=günlük, "hafta"=haftalık ──
GOREVLER = {
    # ── Tek seferlik (ilk kez) ──
    "ilk_giris":    {"puan": 200,  "emoji": "🎉", "baslik": "Hosgeldin",       "aciklama": "Bota ilk kez /start yaz",    "tip": "hic"},
    "ilk_oyun":     {"puan": 100,  "emoji": "🎮", "baslik": "Kumar Kapisi",     "aciklama": "Herhangi bir oyun oyna",      "tip": "hic"},
    "ilk_kazanc":   {"puan": 150,  "emoji": "🏆", "baslik": "Ilk Zafer",        "aciklama": "Bir oyunda kazan",            "tip": "hic"},
    "ilk_davet":    {"puan": 250,  "emoji": "🤝", "baslik": "Sosyal Kelebek",   "aciklama": "1 kisiyi davet et",           "tip": "hic"},
    "bes_davet":    {"puan": 500,  "emoji": "🌟", "baslik": "Topluluk Kurucusu","aciklama": "5 kisi davet et",             "tip": "hic"},
    "vip_ol":       {"puan": 300,  "emoji": "👑", "baslik": "VIP Kulubu",       "aciklama": "10.000 puana ulaş",           "tip": "hic"},
    "sev5":         {"puan": 200,  "emoji": "⭐", "baslik": "Orta Yol",         "aciklama": "Seviye 5'e ulaş",             "tip": "hic"},
    "sev10":        {"puan": 1000, "emoji": "💎", "baslik": "Efsane",           "aciklama": "Seviye 10'a ulaş",            "tip": "hic"},
    "100k_puan":    {"puan": 500,  "emoji": "💰", "baslik": "Zengin Olmak",     "aciklama": "100.000 puan kazan (toplam)", "tip": "hic"},
    # ── Günlük (her gün yapılabilir) ──
    "gunluk_bonus": {"puan": 0,    "emoji": "📅", "baslik": "Sadik Uye",        "aciklama": "/bonus al",                  "tip": "gun"},
    "gunluk_mesaj": {"puan": 10,   "emoji": "💬", "baslik": "Konuşkan",         "aciklama": "Grupta 5 mesaj at",          "tip": "gun", "hedef": 5},
    "gunluk_oyun":  {"puan": 25,   "emoji": "🎲", "baslik": "Kumar Adigi",      "aciklama": "3 oyun oyna",                "tip": "gun", "hedef": 3},
    "gunluk_kazanc":{"puan": 50,   "emoji": "🤑", "baslik": "Kazanan",          "aciklama": "Bir oyunda kazan",           "tip": "gun"},
    # ── Haftalık ──
    "haftalik_bonus":{"puan": 0,   "emoji": "🗓", "baslik": "Haftalik Sadakat", "aciklama": "/hbonus al",                 "tip": "hafta"},
    "haftalik_top3": {"puan": 500, "emoji": "🥇", "baslik": "Top 3",            "aciklama": "Liderlik tablosunda top 3 ol","tip": "hafta"},
    "haftalik_seri": {"puan": 300, "emoji": "🔥", "baslik": "Kor Olmayan Ates", "aciklama": "7 günlük seri yap",          "tip": "hafta"},
}

# ── ROZETLER (seviyeye göre otomatik verilir) ──
ROZETLER = {
    1:  "🌱 Çaylak",    2:  "🔰 Acemi",     3:  "⚔️ Savaşçı",
    4:  "🛡 Kahraman",  5:  "⭐ Usta",      6:  "💫 Şampiyon",
    7:  "🔥 Efsane",    8:  "💎 Elmas",     9:  "👑 Kral",
    10: "🌌 Tanrı",
}

# ── BAŞARIMLAR (özel koşullar) ──
BASARIMLAR = {
    "sansli":   {"emoji": "🍀", "aciklama": "Aynı oyunda 3 kez üst üste kazan"},
    "cesur":    {"emoji": "⚡", "aciklama": "Tek seferde 500+ puan kazan"},
    "fedakar":  {"emoji": "❤️", "aciklama": "100+ puan transfer et"},
    "koleksiyoner": {"emoji": "🗝", "aciklama": "Marketten 3 farklı ürün al"},
}

async def gorev_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = cfg()
    if not c["bakiye_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    tamamlanan = c.get("tamamlanan_gorevler", {}).get(uid, {})
    b = get_bakiye(c, uid)
    sev = hesapla_seviye(c, b["puan"])
    ilerleme = c.get("gorev_ilerleme", {}).get(uid, {})

    hic_satirlar, gun_satirlar, hafta_satirlar = [], [], []
    toplam_puan = 0

    for gid, g in GOREVLER.items():
        tip = g.get("tip", "hic")
        tamamlandi = tamamlanan.get(gid, "")
        hkey = datetime.now().strftime("%Y-W%W")
        puan_str = f"+{g['puan']}" if g["puan"] > 0 else "Otomatik"

        if tip == "hic":
            if tamamlandi:
                satirlar = hic_satirlar
                satirlar.append(f"✅ {g['emoji']} {g['baslik']} — {g['aciklama']}")
            else:
                hic_satirlar.append(f"⭕ {g['emoji']} {g['baslik']} ({puan_str} puan)\n   ↳ {g['aciklama']}")
        elif tip == "gun":
            hedef = g.get("hedef", 1)
            if hedef > 1:
                sayi = ilerleme.get(f"{'mesaj' if 'mesaj' in gid else 'oyun'}_sayi", 0) if ilerleme.get(f"{'mesaj' if 'mesaj' in gid else 'oyun'}_gun") == bugun() else 0
                bar = "█" * min(sayi, hedef) + "░" * max(0, hedef - sayi)
                if tamamlandi == bugun():
                    gun_satirlar.append(f"✅ {g['emoji']} {g['baslik']} [{bar}] {sayi}/{hedef}")
                else:
                    gun_satirlar.append(f"⭕ {g['emoji']} {g['baslik']} ({puan_str} p) [{bar}] {sayi}/{hedef}\n   ↳ {g['aciklama']}")
            else:
                if tamamlandi == bugun():
                    gun_satirlar.append(f"✅ {g['emoji']} {g['baslik']} — Bugün yapıldı")
                else:
                    gun_satirlar.append(f"⭕ {g['emoji']} {g['baslik']} ({puan_str} p)\n   ↳ {g['aciklama']}")
        elif tip == "hafta":
            if tamamlandi == hkey:
                hafta_satirlar.append(f"✅ {g['emoji']} {g['baslik']} — Bu hafta yapıldı")
            else:
                hafta_satirlar.append(f"⭕ {g['emoji']} {g['baslik']} ({puan_str} p)\n   ↳ {g['aciklama']}")

    # Başarımlar
    basarimlar = c.get("basarimlar", {}).get(uid, [])
    bas_str = " ".join([BASARIMLAR[b2]["emoji"] for b2 in basarimlar if b2 in BASARIMLAR]) or "Henüz yok"

    metin = (
        f"<b>Görev Merkezi</b>\n"
        f"{rozet_al(c, uid)} Seviye {sev} | {b['puan']:,} puan\n"
        f"Başarımların: {bas_str}\n\n"
    )
    if hic_satirlar:
        metin += "<b>Tek Seferlik Görevler</b>\n" + "\n".join(hic_satirlar) + "\n\n"
    if gun_satirlar:
        metin += "<b>Günlük Görevler</b>\n" + "\n".join(gun_satirlar) + "\n\n"
    if hafta_satirlar:
        metin += "<b>Haftalık Görevler</b>\n" + "\n".join(hafta_satirlar)

    await update.message.reply_text(metin.strip(), parse_mode="HTML")


async def ver_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin komutu: /ver @kullanıcı [miktar]"""
    if not is_admin(update.effective_user.id): return
    if len(context.args) < 2: return await update.message.reply_text("Kullanım: /ver [user_id] [miktar]")
    c = cfg()
    try:
        uid2 = str(context.args[0]).replace("@","")
        miktar = int(context.args[1])
        yeni = add_puan(c, uid2, f"Kullanıcı {uid2}", miktar)
        await update.message.reply_text(f"✅ +{miktar:,} puan verildi!\nID: {uid2} | Toplam: {yeni:,}")
        try: await context.bot.send_message(int(uid2), f"🎁 <b>+{miktar:,} puan kazandın!</b>\n\n💰 Bakiye: {yeni:,}", parse_mode="HTML")
        except: pass
    except Exception as e: await update.message.reply_text(f"❌ {e}")

async def al_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin komutu: /al [user_id] [miktar] — Puan düş"""
    if not is_admin(update.effective_user.id): return
    if len(context.args) < 2: return await update.message.reply_text("Kullanım: /al [user_id] [miktar]")
    c = cfg()
    try:
        uid2 = str(context.args[0])
        miktar = int(context.args[1])
        yeni = add_puan(c, uid2, f"Kullanıcı {uid2}", -miktar)
        await update.message.reply_text(f"✅ -{miktar:,} puan alındı!\nID: {uid2} | Kalan: {yeni:,}")
    except Exception as e: await update.message.reply_text(f"❌ {e}")

async def sifirla_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: /sifirla [user_id] — Bakiyeyi sıfırla"""
    if not is_admin(update.effective_user.id): return
    if not context.args: return await update.message.reply_text("Kullanım: /sifirla [user_id]")
    c = cfg()
    uid2 = str(context.args[0])
    if uid2 in c["bakiyeler"]:
        c["bakiyeler"][uid2]["puan"] = 0; save(c)
        await update.message.reply_text(f"✅ {uid2} bakiyesi sıfırlandı!")
    else: await update.message.reply_text("❌ Kullanıcı bulunamadı!")

# Mesaj yazınca otomatik puan (aktiflik sistemi)
async def aktiflik_puan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Her mesaj yazan üye küçük puan kazanır"""
    c = cfg()
    if not c["bakiye_aktif"] or not update.message or not update.message.text: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    # Dakikada max 1 kez puan ver (spam önleme)
    son_puan = c.get("son_aktiflik_puani", {}).get(uid, "")
    simdi_dk = datetime.now().strftime("%Y-%m-%d %H:%M")
    if son_puan == simdi_dk: return
    if "son_aktiflik_puani" not in c: c["son_aktiflik_puani"] = {}
    c["son_aktiflik_puani"][uid] = simdi_dk
    add_puan(c, uid, isim, 1)  # Her mesaj = 1 puan (dakikada bir)

# ── PUAN MARKETI ────────────────────────────────────────────────
MARKET_URUNLER = {
    # Rozetler ve Statü
    "vip_rozet":    {"isim": "👑 VIP Rozet",        "fiyat": 2000,  "kategori": "rozet",   "aciklama": "Adinin yaninda VIP rozeti (30 gun)"},
    "altin_rozet":  {"isim": "🥇 Altin Rozet",      "fiyat": 5000,  "kategori": "rozet",   "aciklama": "Altın rozet (30 gun) + %10 bonus"},
    "elmas_rozet":  {"isim": "💎 Elmas Rozet",      "fiyat": 15000, "kategori": "rozet",   "aciklama": "Nadir Elmas rozet (30 gun) + %25 bonus"},
    # Unvanlar
    "ozel_unvan":   {"isim": "🏷 Özel Ünvan",       "fiyat": 1000,  "kategori": "unvan",   "aciklama": "Admin sana ozel unvan verir"},
    "grup_ust":     {"isim": "⚡ Grup Lideri",       "fiyat": 3000,  "kategori": "unvan",   "aciklama": "Bir hafta grup lideri unvani"},
    # Ayricaliklar
    "mesaj_pin":    {"isim": "📌 Mesaj Pinleme",     "fiyat": 500,   "kategori": "ayricalik","aciklama": "Mesajin 24 saat pinlenir"},
    "puan_carpan":  {"isim": "⚡ 2x Puan (1 gun)",  "fiyat": 800,   "kategori": "ayricalik","aciklama": "24 saat 2 kat puan kazan"},
    "bonus_spin":   {"isim": "🎰 Ekstra Spin",       "fiyat": 200,   "kategori": "ayricalik","aciklama": "Casino'da 1 ücretsiz oyun (min bahis ile)"},
    # Korumalar
    "ban_kalkan":   {"isim": "🛡 Ban Kalkan (7 gun)","fiyat": 2500,  "kategori": "koruma",  "aciklama": "1 hafta ban koruması (1 uyarıyı iptal eder)"},
    "warn_sil":     {"isim": "🧹 Uyarı Sil (1 adet)","fiyat": 1500, "kategori": "koruma",  "aciklama": "1 warn silinir"},
}

async def market_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = cfg()
    if not c["bakiye_aktif"]: return
    uid = str(update.effective_user.id)
    b = get_bakiye(c, uid)
    sev = hesapla_seviye(c, b["puan"])

    kategoriler = {}
    for kid, u in MARKET_URUNLER.items():
        kat = u.get("kategori", "diger")
        kategoriler.setdefault(kat, []).append((kid, u))

    kat_emojileri = {"rozet":"🏆","unvan":"🏷","ayricalik":"⚡","koruma":"🛡","diger":"🎁"}
    satirlar = []
    for kat, urunler in kategoriler.items():
        satirlar.append(f"\n<b>{kat_emojileri.get(kat,'🎁')} {kat.title()}</b>")
        for kid, u in urunler:
            alindi = kid in c.get("satin_alinan", {}).get(uid, [])
            durum = "✅ Sahip" if alindi else ("✓ Alınabilir" if b["puan"] >= u["fiyat"] else "🔒")
            satirlar.append(f"{durum} <b>{u['isim']}</b> — {u['fiyat']:,} p\n  ↳ {u.get('aciklama','')}\n  /satin {kid}")

    await update.message.reply_text(
        f"<b>🛒 Puan Marketi</b>\n"
        f"{rozet_al(c, uid)} Bakiyen: <b>{b['puan']:,} puan</b>\n"
        "".join(satirlar),
        parse_mode="HTML"
    )


async def satin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = cfg()
    if not context.args:
        return await update.message.reply_text("Kullanım: /satin [urun_kodu]\n/market ile listeye bak")
    kid = context.args[0]
    if kid not in MARKET_URUNLER:
        return await update.message.reply_text("❌ Ürün bulunamadı! /market ile listeye bak")
    u = MARKET_URUNLER[kid]
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    b = get_bakiye(c, uid)
    if b["puan"] < u["fiyat"]:
        eksik = u["fiyat"] - b["puan"]
        return await update.message.reply_text(
            f"❌ Yetersiz puan!\n\nGerekli: {u['fiyat']:,} | Bakiyen: {b['puan']:,}\n"
            f"Eksik: {eksik:,} puan\n\n/bonus ve /hbonus ile puan kazan!"
        )
    # Satın al
    add_puan(c, uid, isim, -u["fiyat"])
    satin_al = c.setdefault("satin_alinan", {}).setdefault(uid, [])
    if kid not in satin_al: satin_al.append(kid)
    save(c)
    # Başarım: 3 farklı ürün
    if len(set(satin_al)) >= 3:
        if kontrol_basarim(c, uid, isim, "koleksiyoner"):
            save(c)
    yeni_b = get_bakiye(c, uid)
    await update.message.reply_text(
        f"✅ <b>{u['isim']}</b> satın alındı!\n\n"
        f"Ödenen: {u['fiyat']:,} puan\n"
        f"Kalan bakiye: {yeni_b['puan']:,} puan\n\n"
        f"Ürünün aktive edilmesi için admin ile iletişime geç.",
        parse_mode="HTML"
    )
    # Adminlere bildir
    for aid in c.get("adminler", []):
        try:
            await context.bot.send_message(
                aid,
                f"🛒 <b>Market Satışı</b>\n\n"
                f"Kullanıcı: {isim} (<code>{uid}</code>)\n"
                f"Ürün: {u['isim']}\n"
                f"Fiyat: {u['fiyat']:,} puan\n"
                f"Aktive et veya bildir!",
                parse_mode="HTML"
            )
        except: pass


# ══════════════════════════════════════════════════════
# TOPLU MESAJ & DM SİSTEMİ
# ══════════════════════════════════════════════════════

async def dm_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin komutu: /dm [mesaj] — Botla etkileşen tüm üyelere DM at"""
    if not is_admin(update.effective_user.id):
        return
    if not context.args:
        c = cfg()
        kullanici_sayisi = len(c.get("kullanicilar", {}))
        dm_ok = sum(1 for u in c.get("kullanicilar",{}).values() if u.get("dm_ok", True))
        return await update.message.reply_text(
            f"<b>DM Sistemi</b>\n\n"
            f"Kayıtlı kullanıcı: {kullanici_sayisi}\n"
            f"DM alabilir: {dm_ok}\n\n"
            f"Kullanım:\n"
            f"/dm [mesaj] — Tüm kullanıcılara DM at\n"
            f"/dm_filtre vip — Sadece VIP'lere\n"
            f"/dm_filtre aktif — Son 7 gün aktif olanlara\n"
            f"/dm_filtre sev5 — Seviye 5+ olanlara\n\n"
            f"/dm_listesi — Kullanıcı listesi",
            parse_mode="HTML"
        )
    mesaj = " ".join(context.args)
    c = cfg()
    await _toplu_dm_gonder(context, c, mesaj, filtre=None, gonderen=update.effective_user.first_name)

async def dm_filtre_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: /dm_filtre [filtre] [mesaj]"""
    if not is_admin(update.effective_user.id): return
    if not context.args or len(context.args) < 2:
        return await update.message.reply_text(
            "Kullanım: /dm_filtre [filtre] [mesaj]\n\n"
            "Filtreler: vip | aktif | sev5 | sev7 | hepsi"
        )
    filtre = context.args[0]
    mesaj = " ".join(context.args[1:])
    c = cfg()
    await _toplu_dm_gonder(context, c, mesaj, filtre=filtre, gonderen=update.effective_user.first_name)

async def _toplu_dm_gonder(context, c, mesaj, filtre=None, gonderen="Admin"):
    """İç fonksiyon: filtreye göre DM gönder"""
    kullanicilar = c.get("kullanicilar", {})
    if not kullanicilar:
        return

    # Filtre uygula
    hedefler = {}
    bugun_str = bugun()
    yedi_gun_once = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    for uid, u in kullanicilar.items():
        if not u.get("dm_ok", True): continue
        if is_admin(int(uid)): continue  # Adminlere DM atma

        if filtre == "vip" and not is_vip(c, uid): continue
        if filtre == "aktif" and u.get("son_aktif", "") < yedi_gun_once: continue
        if filtre == "sev5":
            b = get_bakiye(c, uid)
            if hesapla_seviye(c, b["puan"]) < 5: continue
        if filtre == "sev7":
            b = get_bakiye(c, uid)
            if hesapla_seviye(c, b["puan"]) < 7: continue
        hedefler[uid] = u

    if not hedefler:
        return

    basarili = 0
    basarisiz = 0
    # Mesajı hazırla
    dm_mesaj = (
        f"<b>📢 Duyuru</b>\n\n"
        f"{mesaj}"
    )
    for uid, u in hedefler.items():
        try:
            await context.bot.send_message(
                int(uid),
                dm_mesaj,
                parse_mode="HTML"
            )
            basarili += 1
            await asyncio.sleep(0.05)  # Rate limit önlemi
        except Exception as e:
            basarisiz += 1
            # DM kapalı ise işaretle
            if "bot was blocked" in str(e).lower() or "chat not found" in str(e).lower():
                c["kullanicilar"][uid]["dm_ok"] = False

    save(c)
    # Sonucu gönderene bildir (admin bot varsa)
    try:
        # Bunu çağıran admin mesajını gönder - ama context.chat_id yok
        # Sadece log
        print(f"[DM] Gönderildi: {basarili} | Başarısız: {basarisiz}")
    except: pass

async def dm_listesi_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: Kayıtlı kullanıcı listesi"""
    if not is_admin(update.effective_user.id): return
    c = cfg()
    kullanicilar = c.get("kullanicilar", {})
    if not kullanicilar:
        return await update.message.reply_text("Henüz kimse kayıtlı.")

    satirlar = []
    for uid, u in list(kullanicilar.items())[:50]:  # Maks 50 göster
        dm = "✉️" if u.get("dm_ok", True) else "🚫"
        b = get_bakiye(c, uid)
        sev = hesapla_seviye(c, b["puan"])
        username = f"@{u['username']}" if u.get("username") else u.get("isim", "?")
        satirlar.append(f"{dm} Sev{sev} {username} — {b['puan']:,} p")

    toplam = len(kullanicilar)
    dm_ok = sum(1 for u in kullanicilar.values() if u.get("dm_ok", True))
    vip_n = sum(1 for uid in kullanicilar if is_vip(c, uid))

    await update.message.reply_text(
        f"<b>Kullanıcı Listesi</b> (toplam {toplam})\n"
        f"DM aktif: {dm_ok} | VIP: {vip_n}\n\n"
        + "\n".join(satirlar[:30]) +
        (f"\n... ve {toplam-30} kişi daha" if toplam > 30 else ""),
        parse_mode="HTML"
    )

async def duyuru_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: /duyuru [mesaj] — Gruba ve tüm kullanıcılara DM"""
    if not is_admin(update.effective_user.id): return
    if not context.args:
        return await update.message.reply_text(
            "Kullanım: /duyuru [mesaj]\n\n"
            "Bu komut:\n"
            "1. Mesajı gruba gönderir\n"
            "2. Tüm kayıtlı kullanıcılara DM atar"
        )
    mesaj = " ".join(context.args)
    c = cfg()
    # Kanallara gönder
    for kanal in c.get("kanallar", []):
        kid = kanal.split("|")[0].strip()
        try:
            await context.bot.send_message(kid, f"📢 <b>DUYURU</b>\n\n{mesaj}", parse_mode="HTML")
        except: pass
    # DM gönder
    await _toplu_dm_gonder(context, c, f"📢 {mesaj}", filtre=None)
    await update.message.reply_text("✅ Duyuru gönderildi!")

async def etkinlik_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: /etkinlik [tip] [sure_saat] — Özel etkinlik başlat"""
    if not is_admin(update.effective_user.id): return
    if not context.args:
        return await update.message.reply_text(
            "<b>Etkinlik Sistemi</b>\n\n"
            "/etkinlik cift_puan 2 — 2 saat çift puan\n"
            "/etkinlik jackpot — Özel jackpot turu\n"
            "/etkinlik yarisme — 1 saatlik puan yarışması\n\n"
            f"Mevcut çarpan: {cfg().get('puan_carpan',1.0)}x",
            parse_mode="HTML"
        )
    tip = context.args[0]
    c = cfg()
    if tip == "cift_puan":
        sure = int(context.args[1]) if len(context.args) > 1 else 2
        c["puan_carpan"] = 2.0
        save(c)
        mesaj = f"🎉 <b>ÇİFT PUAN ETKİNLİĞİ!</b>\n\n{sure} saat boyunca tüm puan kazanımları 2 kat!\n\n/bonus /hbonus ve casino oynayarak avantajdan yararlan!"
        await _toplu_dm_gonder(context, c, mesaj)
        await update.message.reply_text(f"✅ Çift puan etkinliği başlatıldı! ({sure} saat)")
    elif tip == "yarisme":
        # Anlık liderlik bildirimi
        sirali = sorted(c["bakiyeler"].items(), key=lambda x: x[1].get("puan",0), reverse=True)[:5]
        rows = [f"{i+1}. {v.get('isim','?')}: {v.get('puan',0):,}" for i,(u2,v) in enumerate(sirali)]
        mesaj = (
            f"🏆 <b>PUAN YARIŞMASI BAŞLADI!</b>\n\n"
            f"Şu anki liderler:\n" + "\n".join(rows) +
            f"\n\nEn fazla puan kazanan ödül alır!"
        )
        await _toplu_dm_gonder(context, c, mesaj)
        await update.message.reply_text("✅ Yarışma duyurusu gönderildi!")

async def profil_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kullanıcı profili — /profil"""
    c = cfg()
    if not c["bakiye_aktif"]: return
    uid = str(update.effective_user.id)
    b = get_bakiye(c, uid)
    sev = hesapla_seviye(c, b["puan"])
    son_puan, son_sev = sonraki_seviye(c, b["puan"])
    streak = c.get("streak_kayitlar", {}).get(uid, {}).get("gun", 0)
    ref_n = len(c.get("ref_kayitlar", {}).get(uid, []))
    tamamlanan_gorev = len(c.get("tamamlanan_gorevler", {}).get(uid, {}))
    basarimlar = c.get("basarimlar", {}).get(uid, [])
    satin = len(c.get("satin_alinan", {}).get(uid, []))
    vip_tag = " 👑 VIP" if is_vip(c, uid) else ""
    rozet = rozet_al(c, uid)

    if son_puan:
        sev_esik = int(c.get("seviye_esikleri", {}).get(str(sev), 0))
        dolu = int((b["puan"] - sev_esik) / max(1, son_puan - sev_esik) * 12)
        bar = "█" * dolu + "░" * (12 - dolu)
        prog = f"[{bar}] {son_puan - b['puan']:,} kaldı"
    else:
        prog = "████████████ MAKSIMUM!"

    bas_emojiler = " ".join([BASARIMLAR[ba]["emoji"] for ba in basarimlar if ba in BASARIMLAR]) or "—"

    await update.message.reply_text(
        f"{rozet} <b>{update.effective_user.first_name}</b>{vip_tag}\n"
        f"Seviye {sev} → Sev{sev+1 if son_sev else sev}\n"
        f"{prog}\n\n"
        f"💰 Puan: {b['puan']:,} | Toplam: {b.get('toplam',0):,}\n"
        f"🔥 Seri: {streak} gün\n"
        f"🤝 Davet: {ref_n} kişi\n"
        f"📋 Görev: {tamamlanan_gorev} tamamlandı\n"
        f"🛒 Market: {satin} ürün\n"
        f"🏅 Başarımlar: {bas_emojiler}",
        parse_mode="HTML"
    )

async def hbonus_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = cfg()
    if not c["bakiye_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    hkey = datetime.now().strftime("%Y-W%W")
    if c.get("haftalik_bonus_al", {}).get(uid, "") == hkey:
        return await update.message.reply_text("Bu hafta haftalik bonusunu aldin. Pazartesi tekrar gel!")
    haftalik = c.get("haftalik_bonus", 500)
    yeni = add_puan(c, uid, isim, haftalik)
    c.setdefault("haftalik_bonus_al", {})[uid] = hkey
    gorev_tamamla(c, uid, isim, "haftalik_bonus")
    save(c)
    sev = hesapla_seviye(c, yeni)
    await update.message.reply_text(
        f"Haftalik Bonus!\n+{haftalik} puan kazandin!\n"
        f"Seviye {sev} | {yeni:,} puan\n\n"
        f"/bonus ile gunluk bonus da alabilirsin!"
    )


async def seviye_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = cfg()
    esikler = c.get("seviye_esikleri", {})
    uid = str(update.effective_user.id)
    b = get_bakiye(c, uid)
    sev = hesapla_seviye(c, b["puan"])
    son_puan, son_sev = sonraki_seviye(c, b["puan"])
    satirlar = []
    for s, esik in sorted(esikler.items(), key=lambda x: int(x[0])):
        isaret = ">>>" if int(s) == sev else "   "
        rozet = ROZETLER.get(int(s), "")
        satirlar.append(f"{isaret} {rozet} Seviye {s}: {int(esik):,} puan")
    kalan_txt = f"\nSonraki: {son_puan - b['puan']:,} puan kaldi" if son_puan else "\nMAKSIMUM SEVIYE!"
    await update.message.reply_text(
        f"<b>Seviye Tablosu</b>\n\n"
        f"Bakiyen: {b['puan']:,} | Seviye {sev}{kalan_txt}\n\n"
        + "\n".join(satirlar),
        parse_mode="HTML"
    )


async def yardim_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = cfg()
    uid = update.effective_user.id
    if is_admin(uid):
        await update.message.reply_text(
            "<b>Admin Komutlari</b>\n\n"
            "/panel — Admin paneli\n"
            "/ver [id] [miktar] — Puan ver\n"
            "/al [id] [miktar] — Puan al\n"
            "/carpan [sayi] — Puan carpani\n"
            "/dm [mesaj] — Toplu DM\n"
            "/duyuru [mesaj] — Duyuru at\n"
            "/etkinlik cift_puan 2 — Cift puan\n"
            "/dm_listesi — Kullanici listesi",
            parse_mode="HTML"
        )
        return
    cmin = c.get("casino_min_bahis", 10)
    cmax = c.get("casino_max_bahis", 1000)
    gunluk = c.get("gunluk_bonus", 100)
    haftalik = c.get("haftalik_bonus", 500)
    ref_odul = c.get("ref_odul", 10)
    aktiflik = c.get("aktiflik_puan", 2)
    await update.message.reply_text(
        "<b>Komutlar Rehberi</b>\n\n"
        "<b>Bakiye & Puan</b>\n"
        f"/bakiye — Puanin ve seviyen\n"
        f"/profil — Tam profilin\n"
        f"/bonus — Gunluk +{gunluk} puan (seri ile artar)\n"
        f"/hbonus — Haftalik +{haftalik} puan\n"
        "/seviye — Seviye tablosu\n"
        "/top — Liderlik tablosu\n"
        "/transfer [miktar] — Puan gonder\n\n"
        "<b>Gorev & Market</b>\n"
        "/gorev — Gorev merkezi\n"
        "/market — Puan marketi\n"
        f"/ref — Davet linki (+{ref_odul} puan/kisi)\n\n"
        "<b>Casino</b>\n"
        f"Min: {cmin} | Maks: {cmax:,} puan\n"
        "/zar /slot /rulet /balik /mines\n"
        "/tahmin /kart /ya /tombala /savas\n"
        "/bowling /dart /basketbol /penalti\n\n"
        f"<b>Puan Kazan</b>\n"
        f"• Mesaj: {aktiflik} puan/dk\n"
        "• /bonus (gunluk seri)\n"
        "• /hbonus (haftalik)\n"
        "• /gorev (gorevler)\n"
        "• Casino kazanci\n"
        "• Arkadaslarini davet et\n\n"
        "/kurallar | /destek [mesaj] | /btc /eth /ton",
        parse_mode="HTML"
    )


async def carpan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    c = cfg()
    if not context.args:
        return await update.message.reply_text(
            f"Puan Carpani: {c.get('puan_carpan', 1.0)}x\n\n"
            "Kullanim: /carpan [sayi]\nOrnek: /carpan 2.0"
        )
    try:
        p = float(context.args[0])
        c["puan_carpan"] = p
        save(c)
        await update.message.reply_text(f"Puan carpani: {p}x olarak ayarlandi.")
    except:
        await update.message.reply_text("Gecersiz. Ornek: /carpan 2.0")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Admin
    app.add_handler(CommandHandler("start",      start))
    app.add_handler(CommandHandler("iptal",      iptal))
    app.add_handler(CommandHandler("otosil",     otosil_cmd))
    app.add_handler(CommandHandler("emojisil",   emojisil_cmd))
    app.add_handler(CommandHandler("butonsil",   butonsil_cmd))
    app.add_handler(CommandHandler("onayla",     onayla_cmd))
    app.add_handler(CommandHandler("destek",     destek_cmd))
    app.add_handler(CommandHandler("cevap",      cevap_cmd))
    app.add_handler(CommandHandler("yasakekle",  yasakekle_cmd))
    app.add_handler(CommandHandler("yasaksil",   yasaksil_cmd))
    app.add_handler(CommandHandler("anket",      anket_cmd))
    app.add_handler(CommandHandler("ver",        ver_cmd))
    app.add_handler(CommandHandler("al",         al_cmd))
    app.add_handler(CommandHandler("sifirla",    sifirla_cmd))

    # Moderasyon
    app.add_handler(CommandHandler("warn",     warn_cmd))
    app.add_handler(CommandHandler("ban",      ban_cmd))
    app.add_handler(CommandHandler("kick",     kick_cmd))
    app.add_handler(CommandHandler("mute",     mute_cmd))
    app.add_handler(CommandHandler("unmute",   unmute_cmd))
    app.add_handler(CommandHandler("kurallar", kurallar_cmd))

    # Kullanıcı / Ekonomi
    app.add_handler(CommandHandler("bakiye",  bakiye_cmd))
    app.add_handler(CommandHandler("bonus",   bonus_cmd))
    app.add_handler(CommandHandler("hbonus",  hbonus_cmd))
    app.add_handler(CommandHandler("seviye",  seviye_cmd))
    app.add_handler(CommandHandler("yardim",  yardim_cmd))
    app.add_handler(CommandHandler("help",    yardim_cmd))
    app.add_handler(CommandHandler("carpan",  carpan_cmd))
    app.add_handler(CommandHandler("profil",  profil_cmd))
    app.add_handler(CommandHandler("p",       profil_cmd))
    app.add_handler(CommandHandler("dm",          dm_cmd))
    app.add_handler(CommandHandler("dm_filtre",   dm_filtre_cmd))
    app.add_handler(CommandHandler("dm_listesi",  dm_listesi_cmd))
    app.add_handler(CommandHandler("duyuru",      duyuru_cmd))
    app.add_handler(CommandHandler("etkinlik",    etkinlik_cmd))
    app.add_handler(CommandHandler("transfer",transfer_cmd))
    app.add_handler(CommandHandler("top",     top_cmd))
    app.add_handler(CommandHandler("ref",     ref_cmd))
    app.add_handler(CommandHandler("uyeol",   uyeol_cmd))
    app.add_handler(CommandHandler("gorev",   gorev_cmd))
    app.add_handler(CommandHandler("market",  market_cmd))
    app.add_handler(CommandHandler("satin",   satin_cmd))

    # Casino — Temel
    app.add_handler(CommandHandler("zar",     zar_cmd))
    app.add_handler(CommandHandler("tura",    tura_cmd))
    app.add_handler(CommandHandler("slot",    slot_cmd))
    app.add_handler(CommandHandler("rulet",   rulet_cmd))

    # Casino — Ek oyunlar
    app.add_handler(CommandHandler("mines",     mines_cmd))
    app.add_handler(CommandHandler("balik",     balik_cmd))
    app.add_handler(CommandHandler("tahmin",    tahmin_cmd))
    app.add_handler(CommandHandler("kart",      kart_cmd))
    app.add_handler(CommandHandler("ya",        yuksek_alcak_cmd))
    app.add_handler(CommandHandler("tombala",   tombala_cmd))
    app.add_handler(CommandHandler("savas",     savas_cmd))
    app.add_handler(CommandHandler("hediye",    hediye_cmd))

    # Casino — Spor
    app.add_handler(CommandHandler("bowling",   bowling_cmd))
    app.add_handler(CommandHandler("dart",      dart_cmd))
    app.add_handler(CommandHandler("basketbol", basketbol_cmd))
    app.add_handler(CommandHandler("penalti",   futbol_cmd))

    # Kripto
    app.add_handler(CommandHandler("kripto", kripto_cmd))
    app.add_handler(CommandHandler("btc",    btc_cmd))
    app.add_handler(CommandHandler("eth",    eth_cmd))
    app.add_handler(CommandHandler("ton",    ton_cmd))

    # Handlers
    app.add_handler(CallbackQueryHandler(cb_v2))
    app.add_handler(ChatJoinRequestHandler(join_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, yeni_uye))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, mesaj_handler_v2))

    # Jobs
    app.job_queue.run_repeating(oto_job, interval=3600, first=60)
    app.job_queue.run_repeating(rss_job, interval=3600, first=120)

    print("🚀 TG Suite Pro v5.3 başlatıldı!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
