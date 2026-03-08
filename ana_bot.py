"""
╔══════════════════════════════════════════════════════════════════╗
║         TG SUITE PRO — v5.0                                     ║
║  Casino + Moderasyon + Topluluk + Yönetim                       ║
╚══════════════════════════════════════════════════════════════════╝
"""
import logging, random, json, os, asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Poll, BotCommand
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ChatJoinRequestHandler, ContextTypes, filters
)

BOT_TOKEN = "8743351745:AAGgX51IjWqSxNC6HY8yLINyabZ_4Dfq_Ow"
FUTBOL_API_KEY = "4a30a8265295ef0a6ec013630adc4def"  # api-football.com
CONFIG    = "config.json"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT = {
    # Lisans
    "lisans": {"aktif": True, "plan": "pro", "bitis": ""},
    "adminler": [],
    "marka_isim": "SOGTİLLA",
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
    # ── FUTBOL TAHMİN ──
    "sponsorlar": {},
    "futbol_aktif": True,
    # ── QUIZ ──
    "quiz_aktif": True,
    "quiz_sure": 20,           # saniye (her soru)
    "quiz_odul": 150,          # doğru cevap puanı
    "quiz_sorular": [],        # admin ekler veya varsayılan
    "quiz_aktif_oyun": {},     # {chat_id: {soru, katilimcilar, bitis}}
    # ── DÜELLO ──
    "duello_aktif": True,
    "duello_bekleyen": {},     # {duello_id: {meydan_okuyan, rakip, bahis, zaman}}
    # ── JACKPOT ──
    "jackpot_aktif": True,
    "jackpot_havuz": 0,        # biriken puan
    "jackpot_katki": 2,        # her casino oyunundan % kaç kesilir
    "jackpot_son": {},         # {chat_id: son çekiliş zamanı}
    "jackpot_min_katilim": 5,  # minimum katılımcı
    # ── KASAYLA BJ ──
    "kbj_aktif": True,
    "kbj_masalar": {},         # {chat_id: {durum, oyuncular, eller}}
    "futbol_api_key": "4a30a8265295ef0a6ec013630adc4def",  # api-football.com
    "futbol_maclar": {},           # {mac_id: {ev, deplasman, tarih, lig, skor, durum}}
    "futbol_tahminler": {},        # {mac_id: {uid: "1"|"X"|"2"}}
    "futbol_kazanc": {             # doğru tahmin ödülleri
        "1X2": 100,                # maç sonucu tahmini
        "skor": 300,               # tam skor tahmini
        "galibiyet_serisi": 50,    # 3 üst üste doğru = ekstra
    },
    "futbol_tahmin_stats": {},     # {uid: {dogru, yanlis, toplam_puan}}
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
            # API key her zaman güncel kalsın
            if not data.get("futbol_api_key"):
                data["futbol_api_key"] = FUTBOL_API_KEY
            return data
        except: pass
    d = DEFAULT.copy()
    d["futbol_api_key"] = FUTBOL_API_KEY
    save(d); return d

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
        bot_isim = c.get("marka_isim","SOGTİLLA")
        await update.message.reply_text(
            f"<b>Merhaba! {update.effective_user.first_name}</b>\n\n"
            f"Seviye {sev} | {b['puan']:,} puan\n"
            f"{'✅ Bonus alindi' if bonus_alindi else f'/bonus yazarak {c[chr(34)+chr(103)+chr(117)+chr(110)+chr(108)+chr(117)+chr(107)+chr(95)+chr(98)+chr(111)+chr(110)+chr(117)+chr(115)+chr(34)]} puan kazan!'}\n\n"
            f"/yardim — Tum komutlar",
            parse_mode="HTML")
        save(c)
        return
    await update.message.reply_text(
        f"⚡ <b>{c.get('marka_isim','SOGTİLLA')}</b>\n\n"
        f"📢 Kanal: {len(c['kanallar'])}  👥 Üye: {sum(1 for v in c['uyelikler'].values() if v.get('aktif'))}\n"
        f"💸 Bakiye kayıtlı: {len(c['bakiyeler'])}  🎰 Oyun: {c['stats']['casino_oyun']}",
        parse_mode="HTML", reply_markup=ana_kb(c)
    )

async def ana_goster(query, c=None):
    if c is None: c = cfg()
    await query.edit_message_text(
        f"⚡ <b>{c.get('marka_isim','SOGTİLLA')}</b>\n\n"
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
        await q.edit_message_text(f"⚙️ <b>Marka & Admin</b>\n\nBot: {c.get('marka_isim','SOGTİLLA')}\nAdminler:\n{admin_txt}", parse_mode="HTML",
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
    await dm_veya_grup(update, context, 
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
        return await auto_reply(update, f"Bugun bonusunu aldin.\nSerin: {streak} gun. Yarin tekrar gel!")
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
    await dm_veya_grup(update, context, msg, f"🎁 {isim} günlük bonus aldı!")

async def transfer_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c=cfg()
    if not c["bakiye_aktif"]: return
    if len(context.args)<2: return await auto_reply(update, "Kullanım: /transfer @kullanıcı 100")
    uid=str(update.effective_user.id); isim=update.effective_user.first_name
    try:
        miktar=int(context.args[1])
        gonderen=get_bakiye(c, uid)
        if gonderen["puan"]<miktar: return await auto_reply(update, "❌ Yetersiz bakiye!")
        if miktar<=0: return await auto_reply(update, "❌ Geçersiz miktar!")
        # Hedef kullanıcıyı bul (reply veya @username)
        if update.message.reply_to_message:
            hedef_uid=str(update.message.reply_to_message.from_user.id)
            hedef_isim=update.message.reply_to_message.from_user.first_name
        else: return await auto_reply(update, "Transfer için bir mesajı yanıtla!")
        gonderen["puan"]-=miktar
        hedef=get_bakiye(c, hedef_uid); hedef["puan"]+=miktar; hedef["isim"]=hedef_isim
        save(c)
        await update.message.reply_text(f"✅ Transfer tamamlandı!\n{isim} → {hedef_isim}: <b>{miktar:,} puan</b>", parse_mode="HTML")
    except: await dm_veya_grup(update, context, "❌ Hata! Kullanım: /transfer [miktar] (yanıtlayarak)", "💸 Transfer sonucu DM'ine gönderildi!")

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
    await dm_veya_grup(update, context, 
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

# ═══════════════════════════════════════════════════════
#  CASİNO MODÜLÜ v2 — Animasyonlu, gruba spam yok
#  - Tüm oyunlar: önce "oynuyor..." mesajı → edit ile sonuç
#  - Sonuç mesajı sadece o kişiye reply (gruba dağılmaz)
#  - Tüm bug'lar düzeltildi
# ═══════════════════════════════════════════════════════

import asyncio as _asyncio


# ══════════════════════════════════════════════════
# GRUP TEMİZLİĞİ — Casino/bakiye sonuçları DM'e gider
# ══════════════════════════════════════════════════

async def _auto_delete(msg, sure=4):
    """Grup mesajını N saniye sonra sil"""
    await _asyncio.sleep(sure)
    try:
        await msg.delete()
    except:
        pass


async def auto_reply(update: Update, metin: str, parse_mode="HTML", sure=10):
    """Kısa hata/kullanım mesajı: gruplarda sure saniye sonra sil"""
    msg = await update.message.reply_text(metin, parse_mode=parse_mode)
    if update.effective_chat.type != "private":
        _asyncio.create_task(_auto_delete(msg, sure))
    return msg


async def dm_veya_grup(update: Update, context, metin: str,
                       grup_ozet: str = None, parse_mode: str = "HTML",
                       reply_markup=None):
    """
    Private: direkt mesaj (reply_markup ile)
    Grup: tam sonuç DM'e → gruba kısa özet → 8sn sonra sil
    """
    uid = update.effective_user.id
    chat_type = update.effective_chat.type

    if chat_type == "private":
        await update.message.reply_text(metin, parse_mode=parse_mode, reply_markup=reply_markup)
        return

    # DM gönder
    dm_ok = False
    try:
        await context.bot.send_message(uid, metin, parse_mode=parse_mode, reply_markup=reply_markup)
        dm_ok = True
    except Exception as e:
        logger.warning(f"dm_veya_grup DM gönderilemedi uid={uid}: {e}")

    if dm_ok:
        ozet = grup_ozet or "📩 Sonuç DM'ine gönderildi!"
        ozet_msg = await update.message.reply_text(ozet, parse_mode=parse_mode)
        await _auto_delete(ozet_msg, 8)
    else:
        # DM kapalı — gruba yaz, kısa süre sonra sil
        msg = await update.message.reply_text(metin, parse_mode=parse_mode, reply_markup=reply_markup)
        await _auto_delete(msg, 20)


async def dm_anim_veya_grup(update: Update, context, anim_metin: str,
                             sonuc_metin, grup_ozet: str = None,
                             sure: float = 1.2, parse_mode: str = "HTML"):
    """
    Casino sonuçları: chate animasyon → edit ile sonuç → 10sn sonra sil
    Private: anim → edit ile sonuç (kalır)
    grup_ozet parametresi artık kullanılmıyor (geriye dönük uyumluluk)
    """
    uid = update.effective_user.id
    chat_type = update.effective_chat.type

    if chat_type == "private":
        msg = await update.message.reply_text(anim_metin)
        await _asyncio.sleep(sure)
        try:
            await msg.edit_text(sonuc_metin, parse_mode=parse_mode)
        except:
            await update.message.reply_text(sonuc_metin, parse_mode=parse_mode)
        return

    # Grup: animasyon → edit ile sonuç → 10sn sonra sil
    try:
        msg = await update.message.reply_text(anim_metin)
        await _asyncio.sleep(sure)
        try:
            await msg.edit_text(sonuc_metin, parse_mode=parse_mode)
        except:
            await msg.delete()
            msg = await update.message.reply_text(sonuc_metin, parse_mode=parse_mode)
        _asyncio.create_task(_auto_delete(msg, 10))
    except Exception as e:
        logger.error(f"dm_anim_veya_grup: {e}")

async def _casino_anim(msg, metin, sure=1.2):
    """Yükleniyor animasyonu → sonuç"""
    await _asyncio.sleep(sure)
    await msg.edit_text(metin, parse_mode="HTML")

# ── ZAR ──────────────────────────────────────────────
async def zar_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if not context.args:
        return await auto_reply(update, 
            f"🎲 <b>Zar Oyunu</b>\nKullanım: /zar [bahis]\nMin: {c['casino_min_bahis']} | Max: {c['casino_max_bahis']}",
            parse_mode="HTML")
    try:
        hata, bahis = bahis_kontrol(c, uid, context.args[0])
        if hata: return await auto_reply(update, hata)
        _anim_str = "🎲 Zarlar atılıyor..."
        zar1 = random.randint(1,6); zar2 = random.randint(1,6)
        ze = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣"]
        if zar1 > zar2:   kazanc = bahis;          sonuc = "🎉 Kazandın!"
        elif zar1 < zar2: kazanc = -bahis;         sonuc = "😢 Kaybettin!"
        else:             kazanc = int(bahis*1.5); sonuc = "🎊 Beraberlik! +%50 bonus!"
        yeni = add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"] += 1; save(c)
        await dm_anim_veya_grup(update, context, _anim_str,
            f"🎲 <b>Zar Oyunu</b>\n\n"
            f"Sen: {ze[zar1-1]}  Bot: {ze[zar2-1]}\n\n"
            f"{sonuc}\n{'➕' if kazanc>0 else '➖'} <b>{abs(kazanc):,} puan</b>\n"
            f"💰 Bakiye: <b>{yeni:,}</b>")
    except Exception as e:
        await update.message.reply_text(f"❌ Geçerli bir miktar gir!")

# ── YAZI TURA ────────────────────────────────────────
async def tura_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if not context.args:
        return await auto_reply(update, 
            "🪙 <b>Yazı Tura</b>\nKullanım: /tura [bahis] [yazı/tura]\nÖrnek: /tura 100 yazı",
            parse_mode="HTML")
    try:
        hata, bahis = bahis_kontrol(c, uid, context.args[0])
        if hata: return await auto_reply(update, hata)
        tahmin_raw = context.args[1].lower() if len(context.args) > 1 else "yazı"
        # yazı/y/yazi → yazı | tura/t → tura
        if tahmin_raw in ("yazı","yazi","y"): tahmin = "yazı"
        elif tahmin_raw in ("tura","t"): tahmin = "tura"
        else:
            return await auto_reply(update, "❌ Tahmin: yazı veya tura\nÖrnek: /tura 100 yazı")
        _anim_str = "🪙 Para atılıyor..."
        sonuc = random.choice(["yazı","tura"])
        emoji = "🪙" if sonuc == "yazı" else "💫"
        if tahmin == sonuc: kazanc = bahis;  txt = "🎉 Kazandın!"
        else:               kazanc = -bahis; txt = "😢 Kaybettin!"
        yeni = add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"] += 1; save(c)
        await dm_anim_veya_grup(update, context, _anim_str,
            f"{emoji} <b>Yazı Tura</b>\n\n"
            f"Sonuç: <b>{sonuc.upper()}</b>\n"
            f"Tahmin: {tahmin}\n\n"
            f"{txt}\n{'➕' if kazanc>0 else '➖'} <b>{abs(kazanc):,} puan</b>\n"
            f"💰 Bakiye: <b>{yeni:,}</b>")
    except:
        await update.message.reply_text("❌ Geçerli bir miktar gir!")

# ── SLOT ─────────────────────────────────────────────
async def slot_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if not context.args:
        return await auto_reply(update, "🎰 Kullanım: /slot [bahis]")
    try:
        hata, bahis = bahis_kontrol(c, uid, context.args[0])
        if hata: return await auto_reply(update, hata)
        msg = await update.message.reply_text("🎰 Kollar çekiliyor...\n⬛ ⬛ ⬛")
        semboller = ["🍒","🍋","🍊","🍇","💎","7️⃣","⭐","🔔"]
        s = [random.choice(semboller) for _ in range(3)]
        if s[0]==s[1]==s[2]:
            if s[0]=="💎":   kazanc=bahis*10; txt="💎 JACKPOT! 10x!"
            elif s[0]=="7️⃣": kazanc=bahis*7;  txt="7️⃣ SÜPER! 7x!"
            else:            kazanc=bahis*3;  txt="🎉 ÜÇLÜ! 3x!"
        elif s[0]==s[1] or s[1]==s[2] or s[0]==s[2]:
            kazanc=int(bahis*1.5); txt="✨ İkili! 1.5x!"
        else:
            kazanc=-bahis; txt="😢 Kaybettin!"
        yeni = add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"] += 1; save(c)
        await dm_anim_veya_grup(update, context, _anim_str,
            f"🎰 <b>Slot Makinesi</b>\n\n"
            f"┃ {s[0]} {s[1]} {s[2]} ┃\n\n"
            f"{txt}\n{'➕' if kazanc>0 else '➖'} <b>{abs(kazanc):,} puan</b>\n"
            f"💰 Bakiye: <b>{yeni:,}</b>")
    except:
        await update.message.reply_text("❌ Geçerli bir miktar gir!")

# ── RULET ────────────────────────────────────────────
async def rulet_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if not context.args or len(context.args) < 2:
        return await auto_reply(update, 
            "🎡 <b>Rulet</b>\nKullanım: /rulet [bahis] [tahmin]\n\n"
            "Tahmin seçenekleri:\n"
            "• <b>kırmızı / siyah</b> — 2x\n"
            "• <b>tek / çift</b> — 2x\n"
            "• <b>0-36</b> (tam sayı) — 36x\n"
            "Örnek: /rulet 100 kırmızı", parse_mode="HTML")
    try:
        hata, bahis = bahis_kontrol(c, uid, context.args[0])
        if hata: return await auto_reply(update, hata)
        tahmin = " ".join(context.args[1:]).lower()
        _anim_str = "🎡 Rulet dönüyor..."
        sayi = random.randint(0, 36)
        kirmizi = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
        renk = "🔴 Kırmızı" if sayi in kirmizi else ("⚫ Siyah" if sayi>0 else "🟢 Sıfır")
        cift = sayi > 0 and sayi % 2 == 0
        kazanc = 0
        if tahmin in ("kırmızı","kirmizi","red") and sayi in kirmizi:
            kazanc=bahis; txt="🔴 Kırmızı! Kazandın!"
        elif tahmin in ("siyah","black") and sayi>0 and sayi not in kirmizi:
            kazanc=bahis; txt="⚫ Siyah! Kazandın!"
        elif tahmin in ("çift","cift","even") and cift:
            kazanc=bahis; txt="✅ Çift! Kazandın!"
        elif tahmin in ("tek","odd") and sayi>0 and not cift:
            kazanc=bahis; txt="✅ Tek! Kazandın!"
        elif tahmin.isdigit() and int(tahmin)==sayi:
            kazanc=bahis*35; txt=f"🎯 TAM İSABET! 35x!"
        else:
            kazanc=-bahis; txt="😢 Kaybettin!"
        yeni = add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"] += 1; save(c)
        await dm_anim_veya_grup(update, context, _anim_str,
            f"🎡 <b>Rulet</b>\n\n"
            f"Top: <b>{sayi}</b> {renk}\n"
            f"Tahmin: {tahmin}\n\n"
            f"{txt}\n{'➕' if kazanc>0 else '➖'} <b>{abs(kazanc):,} puan</b>\n"
            f"💰 Bakiye: <b>{yeni:,}</b>")
    except:
        await update.message.reply_text("❌ Geçerli bir miktar gir!")

# ── BALİK ────────────────────────────────────────────
async def balik_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🎣 /balik [bahis] — Balık Avı"""
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if not context.args:
        return await auto_reply(update, f"🎣 <b>Balık Avı</b>\nKullanım: /balik [bahis]\nMin: {c['casino_min_bahis']} | Max: {c['casino_max_bahis']}")
    hata, bahis = bahis_kontrol(c, uid, context.args[0])
    if hata: return await auto_reply(update, hata)
    _anim_str = "🎣 Olta atıldı... 🌊"

    SENARYOLAR = [
        # (çarpan, mesaj)
        (0,   f"💥 OLTA KIRILDI! {isim} oltayı attı ama ip koptu... -{bahis:,} puan"),
        (0,   f"🦈 Dev köpekbalığı oltayı kopardı! {isim} hem balık hem olta kaybetti! -{bahis:,} puan"),
        (0,   f"😴 {isim} uyuya kaldı, balık oltayı alıp kaçtı! -{bahis:,} puan"),
        (0.5, f"🐟 Küçük bir balık yakalandı ama kaçtı... {isim} {int(bahis*0.5):,} puan kurtardı"),
        (1.0, f"🐡 {isim} orta boy bir balık yakaladı! +{bahis:,} puan"),
        (1.5, f"🎣 {isim} güzel bir sazan kaptı! +{int(bahis*1.5):,} puan"),
        (2.0, f"🐟 {isim} iri bir levrek yakaladı! +{bahis*2:,} puan"),
        (3.0, f"🦞 {isim} dev bir istakoz çekti! +{bahis*3:,} puan 🎉"),
        (5.0, f"🐋 BALINA! {isim} balina yakaladı!! +{bahis*5:,} puan 🤯"),
        (0,   f"🥾 {isim} eski bir çizme çıkardı... -{bahis:,} puan"),
        (0,   f"🌿 {isim} yosun çekti, balık yoktu... -{bahis:,} puan"),
        (1.0, f"🐠 {isim} renkli bir balık yakaladı! +{bahis:,} puan"),
        (2.5, f"🎣 {isim} kılıç balığı kaptı! +{int(bahis*2.5):,} puan"),
        (6.0, f"🦑 {isim} dev ahtapot çekti!! +{bahis*6:,} puan 🎊"),
    ]
    agirliklar = [8,5,5,10,15,15,12,8,2,8,7,10,8,2]
    senaryo = random.choices(SENARYOLAR, weights=agirliklar, k=1)[0]
    carpan, metin = senaryo
    kazanc = int(bahis * carpan) - (bahis if carpan == 0 else 0)
    if carpan > 0:
        add_puan(c, uid, isim, int(bahis * carpan - bahis) if carpan != 1 else 0)
    else:
        add_puan(c, uid, isim, -bahis)
    jackpot_katki_kes(c, uid, isim, bahis)
    save(c)
    await dm_anim_veya_grup(update, context, _anim_str, f"🎣 {metin}")

async def tahmin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if not context.args or len(context.args) < 2:
        return await auto_reply(update, "🔢 Kullanım: /tahmin [bahis] [1-10]")
    try:
        hata, bahis = bahis_kontrol(c, uid, context.args[0])
        if hata: return await auto_reply(update, hata)
        if not context.args[1].isdigit() or not (1 <= int(context.args[1]) <= 10):
            return await auto_reply(update, "❌ 1 ile 10 arasında sayı gir!")
        tahmin = int(context.args[1])
        _anim_str = "🔢 Sayı seçiliyor..."
        sayi = random.randint(1, 10)
        if tahmin == sayi:
            kazanc = bahis * 8; txt = "🎯 TAM BİLDİN! 8x!"
        elif abs(tahmin - sayi) == 1:
            kazanc = 0; txt = f"😅 Çok yakın! Gerçek: {sayi}"
        else:
            kazanc = -bahis; txt = f"😢 Kaybettin! Gerçek: {sayi}"
        yeni = add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"] += 1; save(c)
        await dm_anim_veya_grup(update, context, _anim_str,
            f"🔢 <b>Sayı Tahmini</b>\n\n"
            f"Sayı: <b>{sayi}</b>  |  Tahmin: {tahmin}\n\n"
            f"{txt}\n{'➕' if kazanc>0 else '➖'} <b>{abs(kazanc):,} puan</b>\n"
            f"💰 Bakiye: <b>{yeni:,}</b>")
    except:
        await update.message.reply_text("❌ Geçerli bir miktar gir!")

# ── KART ─────────────────────────────────────────────
async def kart_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if not context.args:
        return await auto_reply(update, "🃏 Kullanım: /kart [bahis]")
    try:
        hata, bahis = bahis_kontrol(c, uid, context.args[0])
        if hata: return await auto_reply(update, hata)
        _anim_str = "🃏 Kartlar dağıtılıyor..."
        kartlar = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
        deger = {"A":11,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"10":10,"J":10,"Q":10,"K":10}
        oyuncu = random.choices(kartlar, k=2)
        bot_k = random.choices(kartlar, k=2)
        o_puan = sum(deger[k] for k in oyuncu)
        b_puan = sum(deger[k] for k in bot_k)
        if o_puan > 21: o_puan -= 10  # A düzeltme
        if b_puan > 21: b_puan -= 10
        if o_puan > 21:    kazanc=-bahis; txt="💥 Bust! 21 geçtin!"
        elif o_puan==21:   kazanc=int(bahis*1.5); txt="🃏 BLACKJACK! 1.5x!"
        elif o_puan>b_puan or b_puan>21: kazanc=bahis; txt="🎉 Kazandın!"
        elif o_puan==b_puan: kazanc=0; txt="🤝 Beraberlik!"
        else: kazanc=-bahis; txt="😢 Kaybettin!"
        yeni = add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"] += 1; save(c)
        await dm_anim_veya_grup(update, context, _anim_str,
            f"🃏 <b>BlackJack</b>\n\n"
            f"Sen: {' '.join(oyuncu)} = <b>{o_puan}</b>\n"
            f"Bot: {' '.join(bot_k)} = <b>{b_puan}</b>\n\n"
            f"{txt}\n{'➕' if kazanc>0 else '➖'} <b>{abs(kazanc):,} puan</b>\n"
            f"💰 Bakiye: <b>{yeni:,}</b>")
    except:
        await update.message.reply_text("❌ Geçerli bir miktar gir!")

# ── YÜKSEK DÜŞÜK ─────────────────────────────────────
async def yuksek_alcak_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if not context.args or len(context.args) < 2:
        return await auto_reply(update, "📈 Kullanım: /ya [bahis] [yüksek/düşük]")
    try:
        hata, bahis = bahis_kontrol(c, uid, context.args[0])
        if hata: return await auto_reply(update, hata)
        tahmin = context.args[1].lower()
        if tahmin not in ("yüksek","yuksek","y","düşük","dusuk","d"):
            return await auto_reply(update, "❌ yüksek veya düşük yaz\nÖrnek: /ya 100 yüksek")
        _anim_str = "📈 Kart çekiliyor..."
        sayi = random.randint(1,13)
        isim_k = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"][sayi-1]
        yuksek = tahmin in ("yüksek","yuksek","y")
        if (yuksek and sayi>=7) or (not yuksek and sayi<=7):
            kazanc=bahis; txt="✅ Doğru tahmin!"
        else:
            kazanc=-bahis; txt="❌ Yanlış tahmin!"
        if sayi==7: kazanc=0; txt="🤝 Tam 7! Beraberlik!"
        yeni = add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"] += 1; save(c)
        await dm_anim_veya_grup(update, context, _anim_str,
            f"📈 <b>Yüksek / Düşük</b>\n\n"
            f"Kart: <b>{isim_k} ({sayi})</b>\n"
            f"Tahmin: {'Yüksek ⬆️' if yuksek else 'Düşük ⬇️'}\n\n"
            f"{txt}\n{'➕' if kazanc>0 else '➖'} <b>{abs(kazanc):,} puan</b>\n"
            f"💰 Bakiye: <b>{yeni:,}</b>")
    except:
        await update.message.reply_text("❌ Geçerli bir miktar gir!")

# ── TOMBALA ──────────────────────────────────────────
async def tombala_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if not context.args:
        return await auto_reply(update, "🎱 Kullanım: /tombala [bahis]")
    try:
        hata, bahis = bahis_kontrol(c, uid, context.args[0])
        if hata: return await auto_reply(update, hata)
        _anim_str = "🎱 Tombala başlıyor..."
        kart = sorted(random.sample(range(1,90), 15))
        cekilen = sorted(random.sample(range(1,90), 30))
        eslesme = len(set(kart) & set(cekilen))
        if eslesme >= 15:   kazanc=bahis*10; txt="🏆 TOMBALA! 10x!"
        elif eslesme >= 10: kazanc=bahis*3;  txt="🎉 İkinci Çinko! 3x!"
        elif eslesme >= 5:  kazanc=bahis;    txt="✅ Çinko! 1x!"
        else:               kazanc=-bahis;   txt="😢 Kaybettin!"
        yeni = add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"] += 1; save(c)
        await dm_anim_veya_grup(update, context, _anim_str,
            f"🎱 <b>Tombala</b>\n\n"
            f"Eşleşen: <b>{eslesme}/15</b>\n\n"
            f"{txt}\n{'➕' if kazanc>0 else '➖'} <b>{abs(kazanc):,} puan</b>\n"
            f"💰 Bakiye: <b>{yeni:,}</b>", 1.5)
    except:
        await update.message.reply_text("❌ Geçerli bir miktar gir!")

# ── SAVAŞ ────────────────────────────────────────────
async def savas_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """⚔️ /savas [bahis] — Kart Savaşı (sosyal, chate yazar)"""
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if not context.args:
        return await auto_reply(update, "⚔️ <b>Kart Savaşı</b>\nKullanım: /savas [bahis]")
    hata, bahis = bahis_kontrol(c, uid, context.args[0])
    if hata: return await auto_reply(update, hata)

    kartlar = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
    degerler = {k:i+2 for i,k in enumerate(kartlar)}
    oyuncu_k = random.choice(kartlar)
    kasa_k   = random.choice(kartlar)
    o_d = degerler[oyuncu_k]
    k_d = degerler[kasa_k]

    KAZAN_SENARYOLAR = [
        f"⚔️ {isim} kılıcını çekti! {oyuncu_k} vs {kasa_k} — {isim} KAZANDI! +{bahis:,} puan",
        f"🛡 {isim} kalkanıyla savundu, karşı atağa geçti! {oyuncu_k} > {kasa_k} +{bahis:,} puan",
        f"🏹 {isim} ok attı, tam isabet! Kasa {kasa_k} ile direnemedi! +{bahis:,} puan",
        f"🔥 {isim} ateş büyüsü yaptı! {oyuncu_k} kasayı yaktı! +{bahis:,} puan",
        f"⚡ {isim} şimşek hızında saldırdı! {oyuncu_k} vs {kasa_k} — Zafer! +{bahis:,} puan",
    ]
    KAYBET_SENARYOLAR = [
        f"💀 Kasa {kasa_k} ile {isim}'ın {oyuncu_k}'sini ezip geçti! -{bahis:,} puan",
        f"😵 {isim} saldırırken tökezledi, kasa fırsatı kaçırmadı! {kasa_k} > {oyuncu_k} -{bahis:,} puan",
        f"🗡 Kasa'nın {kasa_k}'ı {isim}'ın {oyuncu_k}'sini parçaladı! -{bahis:,} puan",
        f"☠️ {isim} savaştan kaçmaya çalıştı ama yakalandı! {kasa_k} > {oyuncu_k} -{bahis:,} puan",
        f"🌪 Kasa fırtına gibi saldırdı! {isim} dayanamadı! -{bahis:,} puan",
    ]
    BERA_SENARYOLAR = [
        f"🤝 {isim} vs Kasa — {oyuncu_k} = {kasa_k}, tam beraberlik! Kimse hareket etmedi.",
        f"⚖️ Denge bozulmadı! {oyuncu_k} = {kasa_k}, iki taraf da yoruldu.",
    ]

    if o_d > k_d:
        add_puan(c, uid, isim, bahis)
        metin = random.choice(KAZAN_SENARYOLAR)
    elif o_d < k_d:
        add_puan(c, uid, isim, -bahis)
        metin = random.choice(KAYBET_SENARYOLAR)
    else:
        metin = random.choice(BERA_SENARYOLAR)
    jackpot_katki_kes(c, uid, isim, bahis)
    save(c)
    await dm_anim_veya_grup(update, context, "⚔️ Savaş başlıyor...", f"⚔️ {metin}")

async def hediye_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if not context.args:
        return await auto_reply(update, "🎁 Kullanım: /hediye [bahis]")
    try:
        hata, bahis = bahis_kontrol(c, uid, context.args[0])
        if hata: return await auto_reply(update, hata)
        _anim_str = "🎁 Kutu açılıyor..."
        kutular = [
            ("💣","Bomba!",0),("🎁","Küçük Hediye",1.0),
            ("🎀","Güzel Hediye",2.0),("💝","Süper Hediye",3.0),
            ("👑","KRALIYET HEDİYESİ",5.0),("💨","Boş Kutu",0),
        ]
        agirliklar = [15,35,25,15,5,5]
        emoji_k, isim_k, carpan = random.choices(kutular, weights=agirliklar, k=1)[0]
        if carpan == 0:
            kazanc=-bahis; txt=f"{emoji_k} {isim_k}"
        else:
            kazanc=int(bahis*carpan); txt=f"{emoji_k} <b>{isim_k}!</b> {carpan}x!"
        yeni = add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"] += 1; save(c)
        await dm_anim_veya_grup(update, context, _anim_str,
            f"🎁 <b>Hediye Kutusu</b>\n\n"
            f"{txt}\n\n"
            f"{'➕' if kazanc>0 else '➖'} <b>{abs(kazanc):,} puan</b>\n"
            f"💰 Bakiye: <b>{yeni:,}</b>", 1.5)
    except:
        await update.message.reply_text("❌ Geçerli bir miktar gir!")

# ── BOWLİNG ──────────────────────────────────────────
async def bowling_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🎳 /bowling [bahis]"""
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if not context.args:
        return await auto_reply(update, f"🎳 <b>Bowling</b>\nKullanım: /bowling [bahis]")
    hata, bahis = bahis_kontrol(c, uid, context.args[0])
    if hata: return await auto_reply(update, hata)

    SENARYOLAR = [
        (0,   "🙈 Top rampadan çıktı, seyircilere gitti! Güvenlik çağrıldı 🚨 -{bahis} puan"),
        (0,   "💨 {isim} topu attı ama... kanal boş 🕳 -{bahis} puan"),
        (0.5, "😅 {isim} sadece 3 pin devirdi... {kazanc} puan"),
        (1.0, "🎳 {isim} 7 pin! Fena değil. +{bahis} puan"),
        (1.5, "💪 {isim} spare yaptı! Tüm pinler devrildi +{int(bahis*1.5)} puan"),
        (2.0, "🔥 {isim} STRIKE! 10 pin bir vuruşta! +{bahis*2} puan 🎉"),
        (2.5, "⚡ {isim} arka arkaya STRIKE! Turnuva şampiyonu mu bu? +{int(bahis*2.5)} puan"),
        (0,   "🤦 {isim} balonunu fırlattı, top yavaş yavaş kaydı... -{bahis} puan"),
        (0,   "😂 {isim} top yerine ayakkabısını fırlattı! Diskalifiye! -{bahis} puan"),
        (1.2, "😎 {isim} cool bir vuruşla 8 pin! +{int(bahis*1.2)} puan"),
    ]
    agirliklar = [8,8,12,20,18,15,5,7,5,12]
    idx2 = random.choices(range(len(SENARYOLAR)), weights=agirliklar, k=1)[0]
    carpan, sab_metin = SENARYOLAR[idx2]
    kazanc = int(bahis * (carpan - 1)) if carpan > 0 else -bahis
    add_puan(c, uid, isim, kazanc)
    jackpot_katki_kes(c, uid, isim, bahis)
    save(c)
    metin = sab_metin.format(isim=isim, bahis=f"{bahis:,}", kazanc=f"{abs(kazanc):,}",
                             **{k: f"{int(bahis*v):,}" for k,v in
                                [("int(bahis*1.5)",1.5),("int(bahis*2.5)",2.5),("int(bahis*1.2)",1.2),
                                 ("bahis*2",2)]})
    await dm_anim_veya_grup(update, context, "🎳 Top yuvarlanıyor...", f"🎳 {metin}")

async def dart_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🎯 /dart [bahis]"""
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if not context.args:
        return await auto_reply(update, "🎯 <b>Dart</b>\nKullanım: /dart [bahis]")
    hata, bahis = bahis_kontrol(c, uid, context.args[0])
    if hata: return await auto_reply(update, hata)
    DART_S = [
        (0,   lambda b,i: f"😂 {i} dart yerine arkadaşına fırlattı! Diskalifiye! -{b:,}p"),
        (0,   lambda b,i: f"💨 {i}\'nin oku tavana saplandı... -{b:,}p"),
        (0,   lambda b,i: f"🙈 {i} gözlerini kapadı, ok yere düştü! -{b:,}p"),
        (0.5, lambda b,i: f"😅 {i} tahtanın kenarına değdi! +{int(b*0.5):,}p"),
        (1.0, lambda b,i: f"🎯 {i} orta alana vurdu! +{b:,}p"),
        (1.5, lambda b,i: f"💪 {i} çift alan! +{int(b*1.5):,}p"),
        (2.0, lambda b,i: f"🔥 {i} triple 20! Pro gibi! +{b*2:,}p"),
        (3.0, lambda b,i: f"🎯 BULLSEYE! {i} tam ortaya!! +{b*3:,}p 🎉"),
        (0,   lambda b,i: f"🤦 {i}\'nin oku geri döndü, koluna değdi! -{b:,}p"),
        (1.2, lambda b,i: f"😎 {i} çift 16! +{int(b*1.2):,}p"),
    ]
    agirliklar = [8,7,8,12,20,18,12,5,5,13]
    idx2 = random.choices(range(len(DART_S)), weights=agirliklar, k=1)[0]
    carpan, fn = DART_S[idx2]
    metin = fn(bahis, isim)
    kazanc = int(bahis * carpan) - bahis if carpan > 0 else -bahis
    add_puan(c, uid, isim, kazanc)
    jackpot_katki_kes(c, uid, isim, bahis)
    save(c)
    await dm_anim_veya_grup(update, context, "🎯 Ok fırlatılıyor...", f"🎯 {metin}")

async def basketbol_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if not context.args:
        return await auto_reply(update, "🏀 Kullanım: /basketbol [bahis]")
    try:
        hata, bahis = bahis_kontrol(c, uid, context.args[0])
        if hata: return await auto_reply(update, hata)
        _anim_str = "🏀 Top atılıyor..."
        atislar = []
        toplam = 0
        for _ in range(5):
            r = random.random()
            if r < 0.15:   puan=3; atislar.append("🏀 3 Sayı!")
            elif r < 0.5:  puan=2; atislar.append("🏀 2 Sayı!")
            elif r < 0.7:  puan=1; atislar.append("🏀 1 Sayı")
            else:          puan=0; atislar.append("❌ Kaçırdı")
            toplam += puan
        if toplam >= 10: kazanc=int(bahis*2); txt=f"🏆 {toplam} sayı! 2x!"
        elif toplam >= 7: kazanc=bahis; txt=f"🎉 {toplam} sayı! Kazandın!"
        elif toplam >= 4: kazanc=0; txt=f"😐 {toplam} sayı. Beraberlik."
        else: kazanc=-bahis; txt=f"😢 {toplam} sayı. Kaybettin."
        yeni = add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"] += 1; save(c)
        await dm_anim_veya_grup(update, context, _anim_str,
            f"🏀 <b>Basketbol</b>\n\n"
            f"{chr(10).join(atislar)}\n\n"
            f"🏁 Toplam: <b>{toplam} sayı</b>\n"
            f"{txt}\n{'➕' if kazanc>0 else '➖'} <b>{abs(kazanc):,} puan</b>\n"
            f"💰 Bakiye: <b>{yeni:,}</b>")
    except:
        await update.message.reply_text("❌ Geçerli bir miktar gir!")

# ── MİNES ────────────────────────────────────────────
async def mines_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if not context.args:
        return await auto_reply(update, 
            "💣 <b>Mines</b>\nKullanım: /mines [bahis] [mayın_sayısı 1-20]\nÖrnek: /mines 100 5",
            parse_mode="HTML")
    try:
        hata, bahis = bahis_kontrol(c, uid, context.args[0])
        if hata: return await auto_reply(update, hata)
        mayın_sayi = int(context.args[1]) if len(context.args)>1 else 5
        mayın_sayi = max(1, min(20, mayın_sayi))
        _anim_str = "💣 Mayın tarlası hazırlanıyor..."
        hucre = 25
        mayınlar = set(random.sample(range(hucre), mayın_sayi))
        acilan = random.randint(1, hucre - mayın_sayi)
        patladi = False
        for i in range(acilan):
            if random.random() < (mayın_sayi / (hucre - i)):
                patladi = True; break
        carpan = round(1 + (mayın_sayi / (hucre - mayın_sayi)) * acilan, 2)
        if patladi:
            kazanc=-bahis; txt="💥 PATLADI! Mayına bastın!"
        else:
            kazanc=int(bahis*carpan); txt=f"✅ {acilan} güvenli kare! {carpan}x!"
        yeni = add_puan(c, uid, isim, kazanc)
        c["stats"]["casino_oyun"] += 1; save(c)
        await dm_anim_veya_grup(update, context, _anim_str,
            f"💣 <b>Mines</b>\n\n"
            f"Mayın: {mayın_sayi}/25  |  Açılan: {acilan}\n\n"
            f"{txt}\n{'➕' if kazanc>0 else '➖'} <b>{abs(kazanc):,} puan</b>\n"
            f"💰 Bakiye: <b>{yeni:,}</b>", 1.5)
    except:
        await update.message.reply_text("❌ Kullanım: /mines [bahis] [mayın sayısı]")



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

    await dm_veya_grup(update, context, metin.strip(), parse_mode="HTML")


async def ver_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin komutu: /ver @kullanıcı [miktar]"""
    if not is_admin(update.effective_user.id): return
    if len(context.args) < 2: return await auto_reply(update, "Kullanım: /ver [user_id] [miktar]")
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
    if len(context.args) < 2: return await auto_reply(update, "Kullanım: /al [user_id] [miktar]")
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
    if not context.args: return await auto_reply(update, "Kullanım: /sifirla [user_id]")
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

    await dm_veya_grup(update, context, 
        f"<b>🛒 Puan Marketi</b>\n"
        f"{rozet_al(c, uid)} Bakiyen: <b>{b['puan']:,} puan</b>\n"
        "".join(satirlar),
        parse_mode="HTML"
    )


async def satin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = cfg()
    if not context.args:
        return await auto_reply(update, "Kullanım: /satin [urun_kodu]\n/market ile listeye bak")
    kid = context.args[0]
    if kid not in MARKET_URUNLER:
        return await auto_reply(update, "❌ Ürün bulunamadı! /market ile listeye bak")
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
        return await auto_reply(update, 
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
        return await auto_reply(update, 
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
        return await auto_reply(update, "Henüz kimse kayıtlı.")

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
        return await auto_reply(update, 
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

    await dm_veya_grup(update, context, 
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
        return await auto_reply(update, "Bu hafta haftalik bonusunu aldin. Pazartesi tekrar gel!")
    haftalik = c.get("haftalik_bonus", 500)
    yeni = add_puan(c, uid, isim, haftalik)
    c.setdefault("haftalik_bonus_al", {})[uid] = hkey
    gorev_tamamla(c, uid, isim, "haftalik_bonus")
    save(c)
    sev = hesapla_seviye(c, yeni)
    await dm_veya_grup(update, context, 
        f"Haftalik Bonus!\n+{haftalik} puan kazandin!\n"
        f"Seviye {sev} | {yeni:,} puan\n\n"
        f"/bonus ile gunluk bonus da alabilirsin!"
    , "🎁 Haftalık bonus alındı! 📩 DM'e bak.")


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
    await dm_veya_grup(update, context, 
        f"<b>Seviye Tablosu</b>\n\n"
        f"Bakiyen: {b['puan']:,} | Seviye {sev}{kalan_txt}\n\n"
        + "\n".join(satirlar),
        parse_mode="HTML"
    )


async def yardim_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = cfg()
    uid = update.effective_user.id

    # ── ADMİN ──
    if is_admin(uid):
        await update.message.reply_text(
            "<b>🔧 Admin Komutları</b>\n\n"
            "👥 <b>Moderasyon:</b>\n"
            "/ban /kick /mute /unmute /warn /sifirla\n"
            "/temizle [N] — Son N mesajı sil\n\n"
            "💰 <b>Puan Yönetimi:</b>\n"
            "/ver @kisi [puan]  /al @kisi [puan]\n"
            "/carpan @kisi [x] — çarpan belirle\n\n"
            "📢 <b>Duyuru & Etkinlik:</b>\n"
            "/duyuru [metin] — kanala duyuru\n"
            "/etkinlik [metin] — etkinlik başlat\n"
            "/cekilis [ödül] [N] — çekiliş başlat\n\n"
            "⚽ <b>Futbol:</b>\n"
            "/mac_ekle /mac_baslat /mac_bitir /mac_iptal\n"
            "/maclar_cek [tarih] — API'den çek\n"
            "/futbol_api_key [key]\n\n"
            "🧠 <b>Toplu Oyunlar:</b>\n"
            "/quiz [N] /quiz_bitir /quiz_ekle\n"
            "/jackpot_cekilis — jackpot çekilişi\n\n"
            "🔑 <b>Sistem:</b>\n"
            "/istat — bot istatistikleri\n"
            "/panel — bot ayar paneli\n"
            "/dm [uid] [metin] — kullanıcıya DM\n"
            "/dm_filtre /dm_listesi — destek yönetimi\n"
            "/onayla [uid] — üyelik onayla\n"
            "/cevap [uid] — destek cevapla\n\n"
            "📖 /rehber — tam komut rehberi",
            parse_mode="HTML"
        )
        return

    # ── ÜYE ──
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Bakiye & Puan",     callback_data="rehber_bakiye"),
         InlineKeyboardButton("⭐ Seviye & VIP",      callback_data="rehber_seviye")],
        [InlineKeyboardButton("📋 Görevler",           callback_data="rehber_gorev"),
         InlineKeyboardButton("🏅 Başarımlar",         callback_data="rehber_basarim")],
        [InlineKeyboardButton("🎰 Casino (16 oyun)",   callback_data="rehber_casino"),
         InlineKeyboardButton("🛒 Puan Marketi",       callback_data="rehber_market")],
        [InlineKeyboardButton("🎮 Toplu Oyunlar",      callback_data="rehber_topluyun"),
         InlineKeyboardButton("⚽ Futbol Tahmin",      callback_data="rehber_futbol")],
        [InlineKeyboardButton("💡 Strateji & İpucu",  callback_data="rehber_strateji"),
         InlineKeyboardButton("🔧 Diğer Komutlar",    callback_data="rehber_diger")],
    ])
    b = get_bakiye(c, str(uid))
    sev = hesapla_seviye(c, b["puan"])
    rozet = rozet_al(c, str(uid))
    vip_tag = " ⭐VIP" if is_vip(c, str(uid)) else ""
    msg = (
        f"{rozet} <b>{update.effective_user.first_name}{vip_tag}</b>\n"
        f"Seviye {sev} | {b['puan']:,} puan\n\n"
        "<b>📖 Komut Rehberi</b>\n\n"
        "🎯 <b>Hızlı komutlar:</b>\n"
        "/bonus — günlük puan  /bakiye — puanım\n"
        "/kazan — ücretsiz puan  /gorev — görevler\n"
        "/maclar — bugün maçlar  /quiz — bilgi yarışması\n"
        "/duello @kisi — 1v1  /bj — blackjack\n"
        "/istat — istatistikler  /ping — bot durumu\n\n"
        "👇 Kategori seç:"
    )
    await update.message.reply_text(msg, parse_mode="HTML", reply_markup=kb)


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



async def cb_v2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if not q: return
    await q.answer()
    d = q.data
    uid = q.from_user.id

    # ── Admin yetki menüsü
    if d == "m_admin_yetki":
        if admin_seviye(uid) < 3:
            return await q.answer("❌ Sadece Süper Admin erişebilir!", show_alert=True)
        await admin_yetki_menu(q)

    elif d == "yadmin_ekle":
        if admin_seviye(uid) < 3:
            return await q.answer("❌ Yetki yok!", show_alert=True)
        await q.edit_message_text(
            "➕ <b>Yeni Admin Ekle</b>\n\n"
            "Şu formatı yaz:\n<code>USER_ID SEVİYE</code>\n\n"
            "👑 3 = Süper Admin\n🛡 2 = Moderatör\n⭐ 1 = Yardımcı\n\n"
            "Örnek: <code>123456789 2</code>\n\nİptal: /iptal",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data="m_admin_yetki")]]))
        context.user_data["bekle"] = "yadmin_ekle"

    elif d == "yadmin_seviye_sec":
        if admin_seviye(uid) < 3:
            return await q.answer("❌ Yetki yok!", show_alert=True)
        c = cfg()
        SEV_EMOJI = {3: "👑", 2: "🛡", 1: "⭐"}
        adminler_seviye = c.get("adminler_seviye", {})
        rows = [
            [InlineKeyboardButton(
                f"{SEV_EMOJI.get(adminler_seviye.get(str(a), 3), '👑')} {a}",
                callback_data=f"yadmin_sec_{a}"
            )]
            for a in c.get("adminler", [])
        ]
        rows.append([InlineKeyboardButton("🔙 Geri", callback_data="m_admin_yetki")])
        await q.edit_message_text(
            "✏️ Seviyesini değiştireceğin admini seç:",
            reply_markup=InlineKeyboardMarkup(rows))

    elif d.startswith("yadmin_sec_"):
        hedef = d.split("_")[-1]
        await q.edit_message_text(
            f"👤 <b>ID {hedef}</b> için yeni rol seç:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👑 Süper Admin", callback_data=f"yadmin_set_{hedef}_3")],
                [InlineKeyboardButton("🛡 Moderatör",   callback_data=f"yadmin_set_{hedef}_2")],
                [InlineKeyboardButton("⭐ Yardımcı",    callback_data=f"yadmin_set_{hedef}_1")],
                [InlineKeyboardButton("🔙 Geri", callback_data="yadmin_seviye_sec")],
            ]))

    elif d.startswith("yadmin_set_"):
        parcalar = d.split("_")
        hedef_uid, yeni_sev = parcalar[-2], int(parcalar[-1])
        c = cfg()
        if "adminler_seviye" not in c: c["adminler_seviye"] = {}
        c["adminler_seviye"][str(hedef_uid)] = yeni_sev
        save(c)
        SEV_ISIM = {3: "Süper Admin", 2: "Moderatör", 1: "Yardımcı"}
        await q.answer(f"✅ {SEV_ISIM[yeni_sev]} olarak ayarlandı!", show_alert=True)
        await admin_yetki_menu(q)

    elif d == "yadmin_sil_menu":
        if admin_seviye(uid) < 3:
            return await q.answer("❌ Yetki yok!", show_alert=True)
        c = cfg()
        rows = [[InlineKeyboardButton(f"❌ {a}", callback_data=f"yadmin_sil_{a}")] for a in c["adminler"]]
        rows.append([InlineKeyboardButton("🔙 Geri", callback_data="m_admin_yetki")])
        await q.edit_message_text("➖ Silinecek admini seç:", reply_markup=InlineKeyboardMarkup(rows))

    elif d.startswith("yadmin_sil_"):
        aid = int(d.split("_")[-1])
        c = cfg()
        if aid == uid:
            return await q.answer("❌ Kendini silemezsin!", show_alert=True)
        if len(c["adminler"]) <= 1:
            return await q.answer("❌ Son admin silinemez!", show_alert=True)
        if aid in c["adminler"]:
            c["adminler"].remove(aid)
            c.get("adminler_seviye", {}).pop(str(aid), None)
            save(c)
            await q.answer("✅ Admin silindi!", show_alert=True)
        await admin_yetki_menu(q)

    elif d == "yadmin_tablo":
        await q.edit_message_text(
            "📋 <b>Yetki Tablosu</b>\n\n"
            "👑 <b>Süper Admin (3)</b>\n"
            "• Tüm ayarlar, kanal yönetimi\n"
            "• Admin ekle/sil/seviye değiştir\n"
            "• Manuel bakiye ver/al\n"
            "• Lisans yönetimi\n\n"
            "🛡 <b>Moderatör (2)</b>\n"
            "• /ban /kick /mute /unmute\n"
            "• Casino açma/kapama\n"
            "• Anket oluşturma\n\n"
            "⭐ <b>Yardımcı (1)</b>\n"
            "• /warn komutu\n"
            "• Mesaj silme\n"
            "• /kurallar güncelleme",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Geri", callback_data="m_admin_yetki")]]))

    # ── Oyun menüsü
    elif d == "m_oyunlar":
        c = cfg()
        await q.edit_message_text(
            f"🎮 <b>Casino Oyunları</b>\n\nDurum: {'🟢 Aktif' if c['casino_aktif'] else '🔴 Pasif'}\n\n"
            "🎲 /zar  🪙 /tura  🎰 /slot  🎡 /rulet\n"
            "💣 /mines  🎣 /balik  🔢 /tahmin  🃏 /kart\n"
            "📊 /ya  🎱 /tombala  ⚔️ /savas  🎁 /hediye\n"
            "🎳 /bowling  🎯 /dart  🏀 /basketbol  ⚽ /penalti",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔴 Kapat" if c["casino_aktif"] else "🟢 Aç", callback_data="casino_toggle")],
                [InlineKeyboardButton("🔙 Geri", callback_data="ana")],
            ]))

    # ── Geri kalan her callback orijinal cb'ye gider
    else:
        await cb(update, context)


# ── mesaj_handler_v2: Admin giriş bekle + aktiflik puanı ───

async def mesaj_handler_v2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    uid = update.effective_user.id
    bekle = context.user_data.get("bekle")

    # ── Medya (fotoğraf/video/belge) state handler'ları ──
    if bekle and is_admin(uid) and update.message:
        # Fotoğraf
        if update.message.photo and bekle in ("join_foto", "oto_foto"):
            c = cfg()
            foto = update.message.photo[-1]  # En yüksek çözünürlük
            if bekle == "join_foto":
                c["join_medya_tip"] = "foto"
                c["join_medya_id"] = foto.file_id
                save(c); context.user_data["bekle"] = None
                await update.message.reply_text("✅ Karşılama fotoğrafı kaydedildi!")
            elif bekle == "oto_foto":
                c["oto_medya_tip"] = "foto"
                c["oto_medya_id"] = foto.file_id
                save(c); context.user_data["bekle"] = None
                await update.message.reply_text("✅ Otomatik mesaj fotoğrafı kaydedildi!")
            return

        # Video
        if update.message.video and bekle in ("join_video", "oto_video"):
            c = cfg()
            vid = update.message.video
            if bekle == "join_video":
                c["join_medya_tip"] = "video"
                c["join_medya_id"] = vid.file_id
                save(c); context.user_data["bekle"] = None
                await update.message.reply_text("✅ Karşılama videosu kaydedildi!")
            elif bekle == "oto_video":
                c["oto_medya_tip"] = "video"
                c["oto_medya_id"] = vid.file_id
                save(c); context.user_data["bekle"] = None
                await update.message.reply_text("✅ Otomatik mesaj videosu kaydedildi!")
            return

        # Belge/GIF
        if update.message.document and bekle in ("join_foto", "oto_foto", "join_video", "oto_video"):
            c = cfg()
            doc = update.message.document
            tip = "belge"
            if bekle in ("join_foto", "join_video"):
                c["join_medya_tip"] = tip
                c["join_medya_id"] = doc.file_id
                save(c); context.user_data["bekle"] = None
                await update.message.reply_text("✅ Karşılama medyası kaydedildi!")
            else:
                c["oto_medya_tip"] = tip
                c["oto_medya_id"] = doc.file_id
                save(c); context.user_data["bekle"] = None
                await update.message.reply_text("✅ Otomatik mesaj medyası kaydedildi!")
            return

        # Sponsor logo fotoğrafı
        if update.message.photo and bekle == "sponsor_logo":
            foto = update.message.photo[-1]
            context.user_data.setdefault("sponsor_ekle", {})["logo"] = foto.file_id
            context.user_data["bekle"] = None
            await update.message.reply_text("✅ Sponsor logosu kaydedildi!")
            return


    # ── Yeni admin ekleme (yetki sistemi)
    if bekle == "yadmin_ekle" and update.message.text and is_admin(uid):
        try:
            metin_y = update.message.text.strip()
            parcalar = metin_y.split()
            # Format: sadece ID veya "ID SEVİYE"
            yeni_uid = int(parcalar[0].replace("@",""))
            sev = int(parcalar[1]) if len(parcalar) > 1 else 2  # varsayılan seviye 2
            if sev not in [1, 2, 3]:
                sev = 2
            c = cfg()
            if yeni_uid not in c.get("adminler", []):
                c.setdefault("adminler", []).append(yeni_uid)
            c.setdefault("adminler_seviye", {})[str(yeni_uid)] = sev
            save(c)
            context.user_data["bekle"] = None
            SEV_ISIM = {3: "👑 Süper Admin", 2: "🛡 Moderatör", 1: "⭐ Yardımcı"}
            await update.message.reply_text(
                f"✅ Admin eklendi!\n\n"
                f"ID: <code>{yeni_uid}</code>\n"
                f"Rol: <b>{SEV_ISIM[sev]}</b>\n\n"
                f"Seviye değiştirmek için: ID SEVİYE (1/2/3)",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("⚙️ Ayarlara Dön", callback_data="m_ayar")
                ]]))
        except (ValueError, IndexError) as e:
            await auto_reply(update, f"❌ Geçersiz format! Sadece ID yaz\nÖrn: <code>123456789</code>")
        return


    # ── Config state handler'ları (cb_v2 panelinden gelen bekle state'leri) ──
    if bekle and is_admin(uid):
        metin_in = update.message.text.strip() if update.message.text else ""
        c = cfg()
        handled = True

        if bekle == "rss_url":
            if not metin_in.startswith("http"):
                await auto_reply(update, "❌ Geçerli bir URL gir (http ile başlamalı)")
            else:
                c["rss_url"] = metin_in
                save(c); context.user_data["bekle"] = None
                await update.message.reply_text("✅ RSS URL kaydedildi!")

        elif bekle == "marka_isim":
            c["marka_isim"] = metin_in
            save(c); context.user_data["bekle"] = None
            await update.message.reply_text(f"✅ Bot adı: <b>{metin_in}</b>", parse_mode="HTML")

        elif bekle == "kurallar":
            c["kurallar"] = metin_in
            save(c); context.user_data["bekle"] = None
            await update.message.reply_text("✅ Kurallar güncellendi!")

        elif bekle == "join_mesaj":
            c["join_mesaj"] = metin_in
            save(c); context.user_data["bekle"] = None
            await update.message.reply_text("✅ Karşılama mesajı güncellendi!")

        elif bekle == "oto_mesaj":
            c.setdefault("oto_mesajlar", []).append(metin_in)
            save(c); context.user_data["bekle"] = None
            await update.message.reply_text(f"✅ Oto mesaj eklendi! (Toplam: {len(c['oto_mesajlar'])})")

        elif bekle == "emoji_kural":
            c.setdefault("emoji_kurallar", []).append(metin_in)
            save(c); context.user_data["bekle"] = None
            await update.message.reply_text(f"✅ Emoji kuralı eklendi: {metin_in}")

        elif bekle == "kanal_ekle":
            # Format: @kanal veya -100xxx|İsim
            if not (metin_in.startswith("@") or metin_in.startswith("-100")):
                await auto_reply(update, "❌ @kanal_adi veya kanal ID yazmalısın")
            else:
                c.setdefault("kanallar", []).append(metin_in)
                save(c); context.user_data["bekle"] = None
                await update.message.reply_text(f"✅ Kanal eklendi: {metin_in}")

        elif bekle == "admin_ekle":
            try:
                new_uid = int(metin_in.replace("@",""))
                if new_uid not in c.get("adminler", []):
                    c.setdefault("adminler", []).append(new_uid)
                save(c); context.user_data["bekle"] = None
                await update.message.reply_text(
                    f"✅ Admin eklendi: <code>{new_uid}</code>\n\nPanele dönmek için: /start",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("⚙️ Ayarlara Dön", callback_data="m_ayar")
                    ]])
                )
            except:
                await auto_reply(update, "❌ Geçerli bir kullanıcı ID'si gir")

        elif bekle == "oto_aralik":
            try:
                c["oto_aralik"] = int(metin_in) * 3600
                save(c); context.user_data["bekle"] = None
                await update.message.reply_text(f"✅ Oto mesaj aralığı: <b>{metin_in} saat</b>", parse_mode="HTML")
            except: await auto_reply(update, "❌ Sayı gir! (saat cinsinden)")
        elif bekle == "max_uyari":
            try:
                c["max_uyari"] = int(metin_in); save(c); context.user_data["bekle"] = None
                await update.message.reply_text(f"✅ Maks uyarı: <b>{metin_in}</b>", parse_mode="HTML")
            except: await auto_reply(update, "❌ Sayı gir!")
        elif bekle == "ref_odul":
            try:
                c["ref_odul"] = int(metin_in); save(c); context.user_data["bekle"] = None
                await update.message.reply_text(f"✅ Referans ödülü: <b>{metin_in} puan</b>", parse_mode="HTML")
            except: await auto_reply(update, "❌ Sayı gir!")
        elif bekle == "gunluk_bonus":
            try:
                c["gunluk_bonus"] = int(metin_in); save(c); context.user_data["bekle"] = None
                await update.message.reply_text(f"✅ Günlük bonus: <b>{metin_in} puan</b>", parse_mode="HTML")
            except: await auto_reply(update, "❌ Sayı gir!")
        elif bekle == "haftalik_bonus":
            try:
                c["haftalik_bonus"] = int(metin_in); save(c); context.user_data["bekle"] = None
                await update.message.reply_text(f"✅ Haftalık bonus: <b>{metin_in} puan</b>", parse_mode="HTML")
            except: await auto_reply(update, "❌ Sayı gir!")
        elif bekle == "vip_ayar":
            try:
                c["vip_fiyat"] = int(metin_in); save(c); context.user_data["bekle"] = None
                await update.message.reply_text(f"✅ VIP fiyatı: <b>{metin_in} puan</b>", parse_mode="HTML")
            except: await auto_reply(update, "❌ Sayı gir!")
        elif bekle == "aktiflik_puan":
            try:
                c["aktiflik_puan"] = int(metin_in); save(c); context.user_data["bekle"] = None
                await update.message.reply_text(f"✅ Aktiflik puanı: <b>{metin_in}</b>", parse_mode="HTML")
            except: await auto_reply(update, "❌ Sayı gir!")
        elif bekle == "streak_ayar":
            try:
                c["streak_odul"] = int(metin_in); save(c); context.user_data["bekle"] = None
                await update.message.reply_text(f"✅ Streak ödülü: <b>{metin_in} puan</b>", parse_mode="HTML")
            except: await auto_reply(update, "❌ Sayı gir!")
        elif bekle == "uyelik_fiyat":
            try:
                c["uyelik_fiyat"] = int(metin_in); save(c); context.user_data["bekle"] = None
                await update.message.reply_text(f"✅ Üyelik fiyatı: <b>{metin_in} puan</b>", parse_mode="HTML")
            except: await auto_reply(update, "❌ Sayı gir!")
        elif bekle == "captcha_sure":
            try:
                c["captcha_sure"] = int(metin_in); save(c); context.user_data["bekle"] = None
                await update.message.reply_text(f"✅ Captcha süresi: <b>{metin_in} sn</b>", parse_mode="HTML")
            except: await auto_reply(update, "❌ Sayı gir!")
        elif bekle in ("bakiye_ver", "uyelik_cuzdan"):
            try:
                parcalar = metin_in.split()
                uid2, miktar = str(parcalar[0]), int(parcalar[1])
                isim2 = c.get("bakiyeler",{}).get(uid2,{}).get("isim","?")
                add_puan(c, uid2, isim2, miktar)
                save(c); context.user_data["bekle"] = None
                await update.message.reply_text(f"✅ {isim2} +{miktar} puan", parse_mode="HTML")
            except: await auto_reply(update, "❌ Format: user_id miktar")
        elif bekle in ("join_foto", "join_video", "oto_foto", "oto_video", "join_buton"):
            # Medya dosyası bekleniyor — text geldi
            await auto_reply(update, "❌ Lütfen bir dosya/fotoğraf/video gönder!")

        elif bekle == "puan_carpan":
            try:
                c["casino_carpan"] = float(metin_in)
                save(c); context.user_data["bekle"] = None
                await update.message.reply_text(f"✅ Casino çarpanı: <b>{c['casino_carpan']}</b>", parse_mode="HTML")
            except:
                await auto_reply(update, "❌ Sayısal değer gir! (örn: 1.5)")

        elif bekle in ("join_foto", "join_video", "oto_foto", "oto_video"):
            # Medya bekleniyor ama text geldi — state KORUYARAK uyar
            await auto_reply(update, "📸 Lütfen bir fotoğraf veya video gönder! (metin değil)")
        elif bekle == "join_buton":
            # Buton formatı: Metin|URL
            if "|" not in metin_in:
                await auto_reply(update, "❌ Format: <code>Buton Adı|https://link.com</code>", parse_mode="HTML")
            else:
                parts = metin_in.split("|", 1)
                c.setdefault("join_butonlar", []).append([parts[0].strip(), parts[1].strip()])
                save(c); context.user_data["bekle"] = None
                await update.message.reply_text(f"✅ Buton eklendi: <b>{parts[0].strip()}</b>", parse_mode="HTML")

        else:
            handled = False

        if handled:
            return

    # ── Aktiflik puanı (dakikada 1 puan, spam önlemeli)
    c = cfg()
    if c.get("bakiye_aktif") and update.message.text and not is_admin(uid):
        uid_str = str(uid)
        isim = update.effective_user.first_name or "?"
        simdi_dk = datetime.now().strftime("%Y-%m-%d %H:%M")
        son = c.get("son_aktiflik_puani", {}).get(uid_str, "")
        if son != simdi_dk:
            c.setdefault("son_aktiflik_puani", {})[uid_str] = simdi_dk
            add_puan(c, uid_str, isim, 1)

    # ── Geri kalan mesajları orijinal handler'a yolla
    await mesaj_handler(update, context)


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════

async def rehber_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Interaktif komut rehberi — inline butonlu kategori menüsü"""
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Bakiye & Puan",     callback_data="rehber_bakiye"),
         InlineKeyboardButton("⭐ Seviye & VIP",      callback_data="rehber_seviye")],
        [InlineKeyboardButton("📋 Görevler",           callback_data="rehber_gorev"),
         InlineKeyboardButton("🏅 Başarımlar",         callback_data="rehber_basarim")],
        [InlineKeyboardButton("🎰 Casino (16 oyun)",   callback_data="rehber_casino"),
         InlineKeyboardButton("🛒 Puan Marketi",       callback_data="rehber_market")],
        [InlineKeyboardButton("🎮 Toplu Oyunlar",      callback_data="rehber_topluyun"),
         InlineKeyboardButton("⚽ Futbol Tahmin",      callback_data="rehber_futbol")],
        [InlineKeyboardButton("💡 Strateji & İpucu",  callback_data="rehber_strateji"),
         InlineKeyboardButton("🔧 Diğer Komutlar",    callback_data="rehber_diger")],
    ])
    c = cfg()
    b = get_bakiye(c, str(update.effective_user.id))
    sev = hesapla_seviye(c, b["puan"])
    rozet = rozet_al(c, str(update.effective_user.id))
    await update.message.reply_text(
        f"{rozet} <b>Merhaba {update.effective_user.first_name}!</b>\n"
        f"Seviye {sev} | {b['puan']:,} puan\n\n"
        "<b>📖 Komut Rehberi</b>\n"
        "Aşağıdan bir kategori seç:",
        parse_mode="HTML",
        reply_markup=kb
    )

REHBER_ICERIK = {
    "rehber_bakiye": (
        "💰 <b>BAKİYE & PROFİL</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "/bakiye — Puanın, seviyen, VIP durumu\n"
        "/profil (/p) — Tam kart: rozet, başarım, davet, seri\n"
        "/vip — VIP durumu, ilerleme çubuğu, avantajlar\n"
        "/bonus — Günlük bonus (seri ile 220p kadar)\n"
        "/hbonus — Haftalık 500p bonus\n"
        "/kazan — Günlük 3 hak, 20-80p mini görev\n"
        "/transfer @kisi [miktar] — Puan gönder (min 10)\n"
        "/top — Puan sıralaması\n"
        "/ref — Davet linkin (+10p/davet)\n\n"
        "💡 VIP eşiği: 10.000 puan → kazançlarda 1.5x çarpan!"
    ),
    "rehber_seviye": (
        "⭐ <b>SEVİYE & VIP SİSTEMİ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🌱 Sev 1 — Çaylak (0p)\n"
        "🔰 Sev 2 — Acemi (500p)\n"
        "⚔️ Sev 3 — Savaşçı (1.500p)\n"
        "🛡 Sev 4 — Kahraman (3.000p)\n"
        "⭐ Sev 5 — Usta (5.000p)\n"
        "💫 Sev 6 — Şampiyon (8.000p)\n"
        "🔥 Sev 7 — Efsane (12.000p)\n"
        "💎 Sev 8 — Elmas (20.000p)\n"
        "👑 Sev 9 — Kral (35.000p)\n"
        "🌌 Sev 10 — Tanrı (50.000p)\n\n"
        "⭐ <b>VIP:</b> 10.000p → tüm kazançlarda 1.5x\n"
        "/seviye — seviye bilgin + ilerleme çubuğu"
    ),
    "rehber_gorev": (
        "📋 <b>GÖREV MERKEZİ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎯 <b>Tek Seferlik:</b>\n"
        "  ilk_giris +200p | ilk_oyun +100p\n"
        "  ilk_kazanc +150p | ilk_davet +250p\n"
        "  bes_davet +500p | vip_ol +300p\n"
        "  sev5 +200p | sev10 +1000p\n\n"
        "📅 <b>Günlük:</b>\n"
        "  gunluk_bonus +50p | gunluk_mesaj +10p (5 mesaj)\n"
        "  gunluk_oyun +25p (3 oyun) | gunluk_kazanc +50p\n\n"
        "📆 <b>Haftalık:</b>\n"
        "  haftalik_bonus +200p | haftalik_top3 +500p\n"
        "  haftalik_seri +300p (7 günlük seri)\n\n"
        "/gorev — görev durumun ve ilerlemen"
    ),
    "rehber_basarim": (
        "🏆 <b>BAŞARIMLAR</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🍀 <b>Şanslı</b> — 3 üst üste kazanma\n"
        "💪 <b>Cesur</b> — Tek seferde 500p+ kazan\n"
        "🤲 <b>Fedakâr</b> — 100p+ transfer yap\n"
        "🛍 <b>Koleksiyoncu</b> — Marketten 3 farklı ürün al\n\n"
        "Başarımlar profilinde rozet olarak görünür.\n"
        "/profil ile kontrol et!"
    ),
    "rehber_casino": (
        "🎰 <b>CASİNO OYUNLARI (16)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "/zar [bahis] — Zar at, yüksek olan kazanır (1x)\n"
        "/tura [bahis] [yazı/tura] — Para at (1x)\n"
        "/slot [bahis] — Slot makinesi (1.5x-10x)\n"
        "/rulet [bahis] [renk/sayı] — Rulet (2x-35x)\n"
        "/mines [bahis] [mayın] — Mayın tarlası (değişken)\n"
        "/balik [bahis] — Balık avı (0.5x-6x)\n"
        "/tahmin [bahis] [1-10] — Sayı tahmin (8x)\n"
        "/kart [bahis] — BlackJack solo (1x-1.5x)\n"
        "/bj [bahis] — Kasayla BlackJack (butonlu)\n"
        "/ya [bahis] [yüksek/düşük] — Yüksek Düşük (1x)\n"
        "/tombala [bahis] — Tombala (1x-10x)\n"
        "/savas [bahis] — Kart Savaşı (1x)\n"
        "/hediye [bahis] — Hediye Kutusu (0-5x)\n"
        "/bowling [bahis] — Bowling (0-2.5x)\n"
        "/dart [bahis] — Dart (1x-3x)\n"
        "/basketbol [bahis] — Basketbol (0-2x)\n\n"
        "💡 Casino sonuçları DM'ine gelir, grup temiz kalır!"
    ),
    "rehber_topluyun": (
        "🎮 <b>TOPLU & SOSYAL OYUNLAR</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🧠 <b>Bilgi Yarışması</b>\n"
        "  /quiz [soru_sayısı] — Admin başlatır\n"
        "  Doğru cevap: +150p | 20sn süre\n\n"
        "⚔️ <b>Düello (1v1)</b>\n"
        "  /duello @kisi [bahis] — Meydan oku\n"
        "  Kabul ederse zar atılır, kazanan tüm puanı alır\n\n"
        "💰 <b>Jackpot Havuzu</b>\n"
        "  /jackpot — Havuzu gör + katıl\n"
        "  Her casino oyunundan %2 birikir\n\n"
        "🎁 <b>Çekiliş</b>\n"
        "  /cekilis [ödül] [kazanan] — Admin başlatır\n"
        "  Butona bas katıl, 60sn sonra çekiliş\n\n"
        "🔤 <b>Kelime Zinciri</b>\n"
        "  /kelime — Başlat, son harfle devam et (+10p)\n"
        "  /kelime_bitir — Oyunu bitir"
    ),
    "rehber_futbol": (
        "⚽ <b>FUTBOL TAHMİN</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "/maclar — Bugünün maçları (otomatik çekilir)\n"
        "/ftahmin [MAC_ID] [1/X/2] — Maç sonucu tahmin\n"
        "/ftahmin [MAC_ID] [2-1] — Tam skor tahmin (+300p)\n"
        "/tahminlerim — Tahmin geçmişin + istatistik\n"
        "/tahmin_top — Tahmin liderlik tablosu\n\n"
        "🏆 <b>Ödüller:</b>\n"
        "  1/X/2 tahmini: +100p\n"
        "  Tam skor: +300p\n"
        "  3 üst üste doğru: +50p bonus\n\n"
        "📡 Maçlar her sabah 07:00'de otomatik çekilir\n"
        "Takip: Süper Lig 🇹🇷 PL · La Liga · Serie A · UCL"
    ),
    "rehber_market": (
        "🛒 <b>PUAN MARKETİ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🏷 vip_rozet — 2.000p\n"
        "🥇 altin_rozet — 5.000p\n"
        "💎 elmas_rozet — 15.000p\n"
        "✍️ ozel_unvan — 1.000p\n"
        "📌 mesaj_pin — 500p\n"
        "⚡ puan_carpan — 800p (1 günlük 2x)\n"
        "🎰 bonus_spin — 200p (ekstra çevirme)\n"
        "🔝 grup_ust — 3.000p\n"
        "🛡 ban_kalkan — 2.500p\n"
        "❌ warn_sil — 1.500p (1 uyarı sil)\n\n"
        "/market — ürün listesi\n"
        "/satin [urun_id] — satın al"
    ),
    "rehber_strateji": (
        "💡 <b>STRATEJİ & İPUÇLARI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎯 <b>Hızlı puan topla:</b>\n"
        "  1. /bonus + /hbonus her gün/hafta\n"
        "  2. /kazan — günlük 3 kez ücretsiz puan\n"
        "  3. /gorev — görevleri takip et\n"
        "  4. /ref — arkadaş davet et (+250p bonus)\n\n"
        "🎰 <b>Casino stratejisi:</b>\n"
        "  • /slot 200 — düşük riskli, sık oyna\n"
        "  • /rulet 100 kırmızı — %50 şans\n"
        "  • /bj — kasa mantığıyla en düşük ev avantajı\n"
        "  • VIP olunca 1.5x — önce 10k puan biriktir\n\n"
        "⚽ <b>Futbol tahmini:</b>\n"
        "  • Tam skor tahmini 3x daha fazla puan\n"
        "  • 3 üst üste doğru = seri bonusu\n\n"
        "💰 <b>Jackpot:</b> Her oyunda %2 birikir, büyük çekiliş!"
    ),
    "rehber_diger": (
        "🔧 <b>DİĞER KOMUTLAR</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📊 /istat — Bot istatistikleri (üye, casino, jackpot)\n"
        "🏓 /ping — Bot gecikme + uptime\n"
        "🔔 /bildirim — DM bildirimlerini aç/kapat\n"
        "🎫 /uyeol — Ücretli üyelik paketleri\n"
        "🆘 /destek [mesaj] — Destek talebi\n"
        "📜 /kurallar — Grup kuralları\n"
        "💹 /kripto — Kripto fiyatları\n"
        "💹 /btc /eth /ton — Tek coin fiyatı\n"
        "📊 /anket [soru] — Anket başlat\n\n"
        "⚙️ <b>Admin komutları için /yardim yaz</b>"
    ),
    "rehber_ana": (
        "📖 <b>KOMUT REHBERİ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Hangi konuda yardım istiyorsun?"
    ),
}

async def rehber_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rehber inline buton callback'leri"""
    query = update.callback_query
    await query.answer()
    data = query.data

    ANA_MENU_KB = InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Bakiye & Puan",     callback_data="rehber_bakiye"),
         InlineKeyboardButton("⭐ Seviye & VIP",      callback_data="rehber_seviye")],
        [InlineKeyboardButton("📋 Görevler",           callback_data="rehber_gorev"),
         InlineKeyboardButton("🏅 Başarımlar",         callback_data="rehber_basarim")],
        [InlineKeyboardButton("🎰 Casino (16 oyun)",   callback_data="rehber_casino"),
         InlineKeyboardButton("🛒 Puan Marketi",       callback_data="rehber_market")],
        [InlineKeyboardButton("🎮 Toplu Oyunlar",      callback_data="rehber_topluyun"),
         InlineKeyboardButton("⚽ Futbol Tahmin",      callback_data="rehber_futbol")],
        [InlineKeyboardButton("💡 Strateji & İpucu",  callback_data="rehber_strateji"),
         InlineKeyboardButton("🔧 Diğer Komutlar",    callback_data="rehber_diger")],
    ])

    GERI_KB = InlineKeyboardMarkup([[
        InlineKeyboardButton("◀️ Ana Menü", callback_data="rehber_ana")
    ]])

    if data == "rehber_ana":
        await query.edit_message_text(
            "<b>📖 Komut Rehberi</b>\nKategori seç:",
            parse_mode="HTML", reply_markup=ANA_MENU_KB
        )
        return
    if data not in REHBER_ICERIK:
        return
    await query.edit_message_text(
        REHBER_ICERIK[data],
        parse_mode="HTML",
        reply_markup=GERI_KB
    )



# ══════════════════════════════════════════════════════════════════
#  FUTBOL TAHMİN SİSTEMİ
#  - Admin manuel maç ekler (API key opsiyonel)
#  - Üyeler 1/X/2 ve tam skor tahmini yapar
#  - Maç bitince admin sonucu girer → otomatik puan dağıtımı
#  - Liderlik tablosu, kişisel istatistik
# ══════════════════════════════════════════════════════════════════

import uuid as _uuid

# ──────────────────────────────────────────────────────────
# API-FOOTBALL OTOMATİK ÇEKME SİSTEMİ
# dashboard.api-football.com — ücretsiz 100 istek/gün
# ──────────────────────────────────────────────────────────

APIFOOTBALL_URL = "https://v3.football.api-sports.io"

TAKIP_LIGLER = {
    203: "Süper Lig",
    39:  "Premier League",
    140: "La Liga",
    135: "Serie A",
    78:  "Bundesliga",
    61:  "Ligue 1",
    2:   "Champions League",
    3:   "Europa League",
}

async def _api_get(endpoint, params, api_key):
    import aiohttp
    headers = {"x-apisports-key": api_key}
    url = f"{APIFOOTBALL_URL}/{endpoint}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params,
                               timeout=aiohttp.ClientTimeout(total=10)) as r:
            if r.status == 200:
                return await r.json()
            return None

async def api_gunu_maclarini_cek(c, tarih=None):
    api_key = c.get("futbol_api_key", "")
    if not api_key:
        return 0, "API key yok. /futbol_api_key [KEY] ile ekle."
    if tarih is None:
        tarih = datetime.now().strftime("%Y-%m-%d")
    try:
        data = await _api_get("fixtures", {"date": tarih, "timezone": "Europe/Istanbul"}, api_key)
    except Exception as e:
        return 0, f"Bağlantı hatası: {e}"
    if not data or "response" not in data:
        return 0, "API'den veri gelmedi."
    maclar = c.setdefault("futbol_maclar", {})
    eklenen = 0
    guncellenen = 0
    for fixture in data["response"]:
        fix = fixture.get("fixture", {})
        league = fixture.get("league", {})
        teams = fixture.get("teams", {})
        goals = fixture.get("goals", {})
        fix_status = fix.get("status", {})
        league_id = league.get("id")
        if league_id not in TAKIP_LIGLER:
            if league.get("country") not in ("Turkey",): continue
        fix_id = str(fix.get("id", ""))
        ev = teams.get("home", {}).get("name", "?")
        dep = teams.get("away", {}).get("name", "?")
        lig_adi = league.get("name", "Diğer")
        ulke = league.get("country", "")
        tarih_str = fix.get("date", "")[:16].replace("T", " ")
        durum_short = fix_status.get("short", "NS")
        elapsed = fix_status.get("elapsed")
        if durum_short in ("NS", "TBD"): durum = "bekliyor"
        elif durum_short in ("1H", "HT", "2H", "ET", "P", "BT"): durum = "canli"
        elif durum_short in ("FT", "AET", "PEN"): durum = "bitti"
        elif durum_short in ("CANC", "ABD"): durum = "iptal"
        else: durum = "bekliyor"
        ev_gol = goals.get("home")
        dep_gol = goals.get("away")
        skor = f"{ev_gol}-{dep_gol}" if ev_gol is not None and dep_gol is not None and durum in ("canli", "bitti") else ""
        dakika = f"{elapsed}'" if elapsed and durum == "canli" else ""
        mid = f"F{fix_id}"
        if mid in maclar:
            maclar[mid]["durum"] = durum
            if skor: maclar[mid]["skor"] = skor
            maclar[mid]["dakika"] = dakika
            guncellenen += 1
        else:
            maclar[mid] = {
                "ev": ev, "deplasman": dep, "tarih": tarih_str,
                "lig": lig_adi, "ulke": ulke, "durum": durum,
                "skor": skor, "dakika": dakika, "api_id": fix_id, "kaynak": "api",
            }
            eklenen += 1
    return eklenen + guncellenen, f"✅ {eklenen} yeni, {guncellenen} güncellenen maç"

async def api_canli_guncelle(c):
    api_key = c.get("futbol_api_key", "")
    if not api_key: return
    try:
        data = await _api_get("fixtures", {"live": "all"}, api_key)
    except: return
    if not data or "response" not in data: return
    maclar = c.setdefault("futbol_maclar", {})
    for fixture in data["response"]:
        fix = fixture.get("fixture", {})
        goals = fixture.get("goals", {})
        fix_status = fix.get("status", {})
        fix_id = str(fix.get("id", ""))
        mid = f"F{fix_id}"
        if mid not in maclar: continue
        ev_gol = goals.get("home")
        dep_gol = goals.get("away")
        durum_short = fix_status.get("short", "")
        elapsed = fix_status.get("elapsed")
        if ev_gol is not None and dep_gol is not None:
            maclar[mid]["skor"] = f"{ev_gol}-{dep_gol}"
        if elapsed: maclar[mid]["dakika"] = f"{elapsed}'"
        if durum_short in ("FT", "AET", "PEN") and maclar[mid]["durum"] != "bitti":
            maclar[mid]["durum"] = "bitti"
            await _otomatik_puan_dagit(c, mid, maclar[mid]["skor"])
        elif durum_short in ("1H", "HT", "2H", "ET", "P", "BT"):
            maclar[mid]["durum"] = "canli"

async def _otomatik_puan_dagit(c, mid, skor):
    tahminler = c.get("futbol_tahminler", {}).get(mid, {})
    if not tahminler: return
    m = c.get("futbol_maclar", {}).get(mid, {})
    if m.get("puan_dagitildi"): return
    m["puan_dagitildi"] = True
    try:
        ev_g, dep_g = int(skor.split("-")[0]), int(skor.split("-")[1])
    except: return
    if ev_g > dep_g: gercek_1x2 = "1"
    elif ev_g == dep_g: gercek_1x2 = "X"
    else: gercek_1x2 = "2"
    stats = c.setdefault("futbol_tahmin_stats", {})
    odul_1x2 = c.get("futbol_kazanc", {}).get("1X2", 100)
    odul_skor = c.get("futbol_kazanc", {}).get("skor", 300)
    for uid, t_raw in tahminler.items():
        t_tip = t_raw.split("|")[1] if "|" in t_raw else "1X2"
        uye_stats = stats.setdefault(uid, {"dogru": 0, "yanlis": 0, "toplam_puan": 0})
        isim = c.get("bakiyeler", {}).get(uid, {}).get("isim", "?")
        dogru = _tahmin_dogru_mu(t_raw, skor, m)
        if dogru:
            odul = odul_skor if t_tip == "skor" else odul_1x2
            add_puan(c, uid, isim, odul)
            uye_stats["dogru"] += 1
            uye_stats["toplam_puan"] += odul
            seri = uye_stats.get("seri_dogru", 0) + 1
            uye_stats["seri_dogru"] = seri
            if seri >= 3:
                ekstra = c.get("futbol_kazanc", {}).get("galibiyet_serisi", 50)
                add_puan(c, uid, isim, ekstra)
                uye_stats["toplam_puan"] += ekstra
                uye_stats["seri_dogru"] = 0
        else:
            uye_stats["yanlis"] += 1
            uye_stats["seri_dogru"] = 0
    save(c)

async def futbol_gunluk_cek_job(context):
    c = cfg()
    if not c.get("futbol_aktif", True): return
    if not c.get("futbol_api_key", ""): return
    n, msg = await api_gunu_maclarini_cek(c)
    save(c)
    for aid in c.get("adminler", []):
        try:
            await context.bot.send_message(
                aid,
                f"⚽ <b>Günlük Maçlar Güncellendi</b>\n{msg}\n/maclar ile gör",
                parse_mode="HTML"
            )
        except: pass

async def futbol_canli_job(context):
    c = cfg()
    if not c.get("futbol_aktif", True): return
    if not c.get("futbol_api_key", ""): return
    canlilar = [m for m in c.get("futbol_maclar", {}).values() if m.get("durum") == "canli"]
    if not canlilar: return
    await api_canli_guncelle(c)
    save(c)

async def futbol_api_key_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not context.args:
        c = cfg()
        key = c.get("futbol_api_key", "")
        return await update.message.reply_text(
            "<b>⚽ Futbol API Ayarları</b>\n\n"
            f"Mevcut key: {'✅ Aktif (' + key[:8] + '...)' if key else '❌ Yok'}\n\n"
            "<b>Ücretsiz API key nasıl alınır:</b>\n"
            "1. dashboard.api-football.com adresine git\n"
            "2. Kayıt ol (kredi kartı gerekmez)\n"
            "3. API key'ini kopyala\n"
            "4. /futbol_api_key [KEY] ile gir\n\n"
            "Ücretsiz plan: 100 istek/gün\n\n"
            "<b>Takip edilen ligler:</b>\n"
            + "\n".join([f"• {v}" for v in TAKIP_LIGLER.values()]),
            parse_mode="HTML"
        )
    key = context.args[0]
    c = cfg()
    c["futbol_api_key"] = key
    save(c)
    try:
        data = await _api_get("status", {}, key)
        if data and data.get("response"):
            sub = data["response"].get("subscription", {})
            kalan = sub.get("requests", {}).get("current", 0)
            limit = sub.get("requests", {}).get("limit_day", 100)
            await update.message.reply_text(
                f"✅ <b>API Key Kaydedildi!</b>\n\n"
                f"Günlük limit: {limit} istek\n"
                f"Kullanılan: {kalan}\n"
                f"Kalan: {limit - kalan}\n\n"
                f"Şimdi /maclar_cek ile bugünün maçlarını çek!",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text("⚠️ Key kaydedildi ama doğrulanamadı.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Key kaydedildi. Hata: {e}")

async def maclar_cek_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    c = cfg()
    tarih = context.args[0] if context.args else None
    if not c.get("futbol_api_key", ""):
        return await update.message.reply_text(
            "❌ API key yok!\n/futbol_api_key [KEY] ile ekle.\n\n"
            "Ücretsiz key: dashboard.api-football.com"
        )
    msg_obj = await update.message.reply_text("⏳ Maçlar çekiliyor...")
    n, sonuc = await api_gunu_maclarini_cek(c, tarih)
    save(c)
    maclar = c.get("futbol_maclar", {})
    bugun = tarih or datetime.now().strftime("%Y-%m-%d")
    bugun_maclar = [(mid, m) for mid, m in maclar.items() if m.get("tarih", "").startswith(bugun)]
    satirlar = [f"⚽ <b>Maçlar Güncellendi</b>\n{sonuc}\n"]
    for mid, m in sorted(bugun_maclar, key=lambda x: x[1].get("tarih", ""))[:15]:
        de = mac_durum_emoji(m.get("durum", "bekliyor"))
        skor = f" {m['skor']}" if m.get("skor") else ""
        dk = f" {m.get('dakika', '')}" if m.get("dakika") else ""
        satirlar.append(f"{de} {m.get('ev', '?')} vs {m.get('deplasman', '?')}{skor}{dk}")
    await msg_obj.edit_text("\n".join(satirlar[:20]), parse_mode="HTML")

async def futbol_ligler_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    ligler_str = "\n".join([f"• {v} (ID: {k})" for k, v in TAKIP_LIGLER.items()])
    await update.message.reply_text(
        f"<b>⚽ Takip Edilen Ligler</b>\n\n{ligler_str}\n\n"
        "Lig ID'leri için: api-football.com/documentation",
        parse_mode="HTML"
    )



LIG_EMOJILERI = {
    "Premier League": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "La Liga": "🇪🇸", "Serie A": "🇮🇹",
    "Bundesliga": "🇩🇪", "Ligue 1": "🇫🇷", "Süper Lig": "🇹🇷",
    "Champions League": "🌟", "Europa League": "🟠",
    "Conference League": "🔵", "Dünya Kupası": "🌍",
    "diğer": "⚽",
}

def lig_emoji(lig):
    for k,v in LIG_EMOJILERI.items():
        if k.lower() in lig.lower(): return v
    return "⚽"

def mac_id_olustur():
    return _uuid.uuid4().hex[:6].upper()

def mac_durum_emoji(durum):
    return {"bekliyor":"⏳","canli":"🔴","bitti":"✅","iptal":"❌"}.get(durum,"⚽")

def format_mac(mid, m, c=None, uid=None):
    """Tek maç satırı formatla"""
    de = mac_durum_emoji(m.get("durum","bekliyor"))
    le = lig_emoji(m.get("lig",""))
    tarih = m.get("tarih","")[:16] if m.get("tarih") else "?"
    skor = m.get("skor","")
    skor_str = f"  <b>{skor}</b>" if skor else ""
    tahmin_str = ""
    if c and uid:
        t = c.get("futbol_tahminler",{}).get(mid,{}).get(uid,"")
        if t:
            secim_emoji = {"1":"🔵","X":"🟡","2":"🔴"}.get(t.split("|")[0],""  )
            tahmin_str = f"  {secim_emoji} Tahminim: <b>{t}</b>"
    return (
        f"{de} <b>[{mid}]</b> {le} {m.get('lig','')}\n"
        f"   🏠 {m.get('ev','?')}  vs  {m.get('deplasman','?')} 🚌{skor_str}\n"
        f"   🕐 {tarih}{tahmin_str}"
    )

# ─────────────────────────────────────────
# KOMUTLAR
# ─────────────────────────────────────────

async def maclar_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """⚽ /maclar — Aktif/bekleyen maçları listele + tahmin butonları"""
    c = cfg()
    if not c.get("futbol_aktif", True): return
    uid = str(update.effective_user.id)
    maclar = c.get("futbol_maclar", {})

    if not maclar:
        return await update.message.reply_text(
            "⚽ <b>Maç Takvimi</b>\n\n"
            "Henüz maç eklenmedi.\n"
            "Admin /mac_ekle komutuyla maç ekleyebilir.",
            parse_mode="HTML"
        )

    bekleyen, canli, biten = [], [], []
    for mid, m in maclar.items():
        d = m.get("durum","bekliyor")
        if d == "canli": canli.append((mid,m))
        elif d == "bitti": biten.append((mid,m))
        else: bekleyen.append((mid,m))

    metin = "⚽ <b>Maç Takvimi</b>\n━━━━━━━━━━━━━━━━━━━━━\n"

    if canli:
        metin += "\n🔴 <b>CANLI MAÇLAR</b>\n"
        for mid,m in canli:
            metin += format_mac(mid, m, c, uid) + "\n\n"

    if bekleyen:
        metin += "\n⏳ <b>YAKLAŞAN MAÇLAR</b>\n"
        for mid,m in bekleyen:
            metin += format_mac(mid, m, c, uid) + "\n\n"

    if biten:
        metin += "\n✅ <b>TAMAMLANAN MAÇLAR</b>\n"
        for mid,m in list(reversed(biten))[:5]:
            metin += format_mac(mid, m, c, uid) + "\n\n"

    metin += "\n💡 Tahmin için: /tahmin [MAC_ID] [1|X|2]\n"
    metin += "🏆 Liderlik: /tahmin_top  |  İstatistik: /tahmin_stat"

    # Inline butonlar — bekleyen maçlar için hızlı tahmin
    butonlar = []
    for mid, m in bekleyen[:4]:
        butonlar.append([
            InlineKeyboardButton(
                f"⚽ {m.get('ev','?')[:12]} vs {m.get('deplasman','?')[:12]} [{mid}]",
                callback_data=f"mac_sec_{mid}"
            )
        ])
    if butonlar:
        metin += "\n\n👇 Hızlı tahmin için maça tıkla:"
        await update.message.reply_text(metin, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(butonlar))
    else:
        await update.message.reply_text(metin, parse_mode="HTML")


async def futbol_tahmin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """⚽ /ftahmin [MAC_ID] [1|X|2] veya /ftahmin [MAC_ID] [ev_gol]-[dep_gol]"""
    c = cfg()
    if not c.get("futbol_aktif", True): return
    if not c.get("bakiye_aktif"): return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name

    if not context.args or len(context.args) < 2:
        return await auto_reply(update, 
            "⚽ <b>Tahmin Yap</b>\n\n"
            "Kullanım:\n"
            "/tahmin [MAC_ID] 1  — Ev sahibi kazanır\n"
            "/tahmin [MAC_ID] X  — Beraberlik\n"
            "/tahmin [MAC_ID] 2  — Deplasman kazanır\n"
            "/tahmin [MAC_ID] 2-1  — Tam skor (Ev 2, Dep 1)\n\n"
            "/maclar ile maç listesine bak",
            parse_mode="HTML"
        )

    mid = context.args[0].upper()
    maclar = c.get("futbol_maclar", {})
    if mid not in maclar:
        return await auto_reply(update, f"❌ [{mid}] ID'li maç bulunamadı. /maclar ile kontrol et.")

    m = maclar[mid]
    if m.get("durum") == "bitti":
        return await auto_reply(update, "❌ Bu maç tamamlandı, tahmin yapılamaz!")
    if m.get("durum") == "canli":
        return await auto_reply(update, "❌ Maç başladı, tahmin kapalı!")

    secim_raw = context.args[1].upper()
    # Tam skor mu (2-1 gibi) yoksa 1/X/2 mi?
    if "-" in secim_raw and secim_raw != "X":
        # Tam skor tahmini
        parca = secim_raw.split("-")
        if len(parca) != 2 or not all(p.isdigit() for p in parca):
            return await auto_reply(update, "❌ Geçersiz skor formatı. Örnek: /tahmin ABC123 2-1")
        secim = secim_raw  # "2-1"
        tip = "skor"
        odul = c.get("futbol_kazanc",{}).get("skor", 300)
        secim_goster = f"🎯 Tam Skor: {m.get('ev','?')} <b>{secim}</b> {m.get('deplasman','?')}"
    elif secim_raw in ("1","X","2"):
        secim = secim_raw
        tip = "1X2"
        odul = c.get("futbol_kazanc",{}).get("1X2", 100)
        label = {"1": f"🏠 {m.get('ev','?')} kazanır", "X": "🤝 Beraberlik", "2": f"🚌 {m.get('deplasman','?')} kazanır"}
        secim_goster = label[secim]
    else:
        return await auto_reply(update, "❌ Geçersiz tahmin. 1, X, 2 veya 2-1 gibi skor gir.")

    # Kaydet
    tahminler = c.setdefault("futbol_tahminler", {})
    mac_tahminler = tahminler.setdefault(mid, {})

    # Önceki tahmin varsa güncelle
    onceki = mac_tahminler.get(uid, "")
    mac_tahminler[uid] = f"{secim}|{tip}"
    save(c)

    degisti_str = f"\n<i>(Önceki tahmin '{onceki.split('|')[0]}' değiştirildi)</i>" if onceki else ""
    toplam_tahmin = len(mac_tahminler)

    await update.message.reply_text(
        f"✅ <b>Tahmin Kaydedildi!</b>{degisti_str}\n\n"
        f"🏟 {m.get('ev','?')} vs {m.get('deplasman','?')}\n"
        f"📌 Tahminин: {secim_goster}\n"
        f"🏆 Doğru olursa: <b>+{odul} puan</b>\n\n"
        f"👥 Bu maçta toplam {toplam_tahmin} tahmin var\n"
        f"📊 /tahminlerim ile tüm tahminlerini gör",
        parse_mode="HTML"
    )


async def tahminlerim_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📊 /tahminlerim — Kişisel tahmin geçmişi"""
    c = cfg()
    if not c.get("futbol_aktif", True): return
    uid = str(update.effective_user.id)
    maclar = c.get("futbol_maclar", {})
    tahminler = c.get("futbol_tahminler", {})
    stats = c.get("futbol_tahmin_stats", {}).get(uid, {})

    satirlar = []
    for mid, mac_t in tahminler.items():
        if uid not in mac_t: continue
        m = maclar.get(mid, {})
        t_raw = mac_t[uid]
        t_sec = t_raw.split("|")[0]
        durum = m.get("durum","bekliyor")
        skor = m.get("skor","")

        if durum == "bitti" and skor:
            # Doğru mu?
            dogru = _tahmin_dogru_mu(t_raw, skor, m)
            sonuc = "✅" if dogru else "❌"
        elif durum == "canli":
            sonuc = "🔴"
        else:
            sonuc = "⏳"

        satirlar.append(
            f"{sonuc} <b>[{mid}]</b> {m.get('ev','?')} vs {m.get('deplasman','?')}\n"
            f"   Tahmin: <b>{t_sec}</b>  |  Skor: {skor or '?'}"
        )

    dogru_n = stats.get("dogru", 0)
    yanlis_n = stats.get("yanlis", 0)
    toplam_puan = stats.get("toplam_puan", 0)
    oran = f"%{int(dogru_n/(dogru_n+yanlis_n)*100)}" if (dogru_n+yanlis_n) > 0 else "%0"

    metin = (
        f"📊 <b>Tahmin İstatistiklerin</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Doğru: {dogru_n}  ❌ Yanlış: {yanlis_n}  🎯 Oran: {oran}\n"
        f"🏆 Tahminlerden Kazanılan: {toplam_puan:,} puan\n\n"
    )
    if satirlar:
        metin += "\n".join(satirlar)
    else:
        metin += "Henüz tahmin yapmadın.\n/maclar ile maçlara bak!"

    await update.message.reply_text(metin, parse_mode="HTML")


async def tahmin_top_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🏆 /tahmin_top — Tahmin liderlik tablosu"""
    c = cfg()
    if not c.get("futbol_aktif", True): return
    stats = c.get("futbol_tahmin_stats", {})
    if not stats:
        return await auto_reply(update, "Henüz tahmin istatistiği yok. /maclar ile tahmin yap!")

    sirali = sorted(stats.items(),
        key=lambda x: (x[1].get("dogru",0), x[1].get("toplam_puan",0)),
        reverse=True)

    uid = str(update.effective_user.id)
    metin = "🏆 <b>Tahmin Liderlik Tablosu</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
    madalya = ["🥇","🥈","🥉"]
    kendi_sira = None

    for i, (u, s) in enumerate(sirali[:10]):
        d = s.get("dogru",0)
        y = s.get("yanlis",0)
        tp = s.get("toplam_puan",0)
        oran = f"%{int(d/(d+y)*100)}" if (d+y) > 0 else "%0"
        isim = c.get("bakiyeler",{}).get(u,{}).get("isim","?")
        icon = madalya[i] if i < 3 else f"{i+1}."
        b_str = rozet_al(c, u)
        kendi = " ← Sen" if u == uid else ""
        metin += f"{icon} {b_str} {isim}  {oran} ({d}✅/{d+y})\n   +{tp:,} puan{kendi}\n"
        if u == uid:
            kendi_sira = i+1

    if kendi_sira is None and uid in stats:
        s = stats[uid]
        d = s.get("dogru",0); y = s.get("yanlis",0)
        tp = s.get("toplam_puan",0)
        sira = next((i+1 for i,(u,_) in enumerate(sirali) if u==uid), "?")
        metin += f"\n...\n{sira}. Sen — {d}✅/{d+y}  +{tp:,} puan"
    elif kendi_sira is None:
        metin += "\nSenin henüz istatistiğin yok — /maclar ile tahmin yap!"

    await update.message.reply_text(metin, parse_mode="HTML")


# ─────────────────────────────────────────
# ADMİN KOMUTLARI
# ─────────────────────────────────────────

async def mac_ekle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: /mac_ekle — Maç ekleme wizard'ı başlat"""
    if not is_admin(update.effective_user.id): return
    await update.message.reply_text(
        "⚽ <b>Maç Ekle</b>\n\n"
        "Format:\n"
        "<code>/mac_ekle [Ev Takımı] | [Deplasman] | [TT-AA SS:DD] | [Lig]</code>\n\n"
        "Örnek:\n"
        "<code>/mac_ekle Galatasaray | Fenerbahçe | 08-03 20:00 | Süper Lig</code>\n\n"
        "Lig örnekleri: Süper Lig, Premier League, La Liga, Serie A, Bundesliga, Champions League",
        parse_mode="HTML"
    )

async def mac_ekle_isle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: Doğrudan maç ekle"""
    if not is_admin(update.effective_user.id): return
    if not context.args:
        return await mac_ekle_cmd(update, context)

    metin = " ".join(context.args)
    parca = [p.strip() for p in metin.split("|")]
    if len(parca) < 3:
        return await update.message.reply_text(
            "❌ Format hatalı!\n"
            "/mac_ekle Galatasaray | Fenerbahçe | 08-03 20:00 | Süper Lig"
        )

    ev = parca[0]
    dep = parca[1]
    tarih_raw = parca[2]
    lig = parca[3] if len(parca) > 3 else "diğer"

    # Tarih formatla
    yil = datetime.now().year
    try:
        tarih = datetime.strptime(f"{yil}-{tarih_raw}", "%Y-%m-%d %H:%M").strftime("%Y-%m-%d %H:%M")
    except:
        tarih = tarih_raw

    mid = mac_id_olustur()
    c = cfg()
    c.setdefault("futbol_maclar", {})[mid] = {
        "ev": ev, "deplasman": dep, "tarih": tarih,
        "lig": lig, "durum": "bekliyor", "skor": "",
    }
    save(c)

    le = lig_emoji(lig)
    await update.message.reply_text(
        f"✅ <b>Maç Eklendi!</b>\n\n"
        f"🆔 Maç ID: <code>{mid}</code>\n"
        f"{le} Lig: {lig}\n"
        f"🏠 {ev}  vs  🚌 {dep}\n"
        f"🕐 {tarih}\n\n"
        f"Komutlar:\n"
        f"/mac_baslat {mid} — Canlı yap\n"
        f"/mac_bitir {mid} [skor] — Bitir ve puan dağıt\n"
        f"/mac_iptal {mid} — İptal et",
        parse_mode="HTML"
    )

    # Kanallara/gruba duyur
    for kanal in c.get("kanallar", []):
        kid = kanal.split("|")[0].strip()
        try:
            await context.bot.send_message(
                kid,
                f"⚽ <b>Yeni Maç Eklendi!</b>\n\n"
                f"{le} <b>{lig}</b>\n"
                f"🏠 <b>{ev}</b>  vs  🚌 <b>{dep}</b>\n"
                f"🕐 {tarih}\n\n"
                f"🎯 Tahmin için: /tahmin {mid} [1|X|2]\n"
                f"📋 /maclar ile tüm maçlara bak",
                parse_mode="HTML"
            )
        except: pass


async def mac_baslat_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: /mac_baslat [MAC_ID] — Maçı canlı yap"""
    if not is_admin(update.effective_user.id): return
    if not context.args:
        return await auto_reply(update, "Kullanım: /mac_baslat [MAC_ID]")
    mid = context.args[0].upper()
    c = cfg()
    maclar = c.get("futbol_maclar", {})
    if mid not in maclar:
        return await auto_reply(update, f"❌ [{mid}] bulunamadı.")
    maclar[mid]["durum"] = "canli"
    save(c)
    m = maclar[mid]
    await update.message.reply_text(
        f"🔴 <b>Maç Canlı!</b>\n\n"
        f"[{mid}] {m['ev']} vs {m['deplasman']}\n"
        f"Tahmin girişi kapatıldı.",
        parse_mode="HTML"
    )


async def mac_bitir_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: /mac_bitir [MAC_ID] [ev_gol-dep_gol] — Sonuç gir, puan dağıt"""
    if not is_admin(update.effective_user.id): return
    if not context.args or len(context.args) < 2:
        return await auto_reply(update, 
            "Kullanım: /mac_bitir [MAC_ID] [skor]\n"
            "Örnek: /mac_bitir ABC123 2-1"
        )
    mid = context.args[0].upper()
    skor = context.args[1]
    c = cfg()
    maclar = c.get("futbol_maclar", {})
    if mid not in maclar:
        return await auto_reply(update, f"❌ [{mid}] bulunamadı.")

    # Skor doğrula
    if "-" not in skor or not all(p.isdigit() for p in skor.split("-")):
        return await auto_reply(update, "❌ Geçersiz skor. Örnek: 2-1")

    maclar[mid]["durum"] = "bitti"
    maclar[mid]["skor"] = skor
    m = maclar[mid]

    # Skoru parse et → 1X2 sonucunu belirle
    ev_gol, dep_gol = int(skor.split("-")[0]), int(skor.split("-")[1])
    if ev_gol > dep_gol: gercek_1x2 = "1"
    elif ev_gol == dep_gol: gercek_1x2 = "X"
    else: gercek_1x2 = "2"

    # Tahminleri değerlendir
    tahminler = c.get("futbol_tahminler", {}).get(mid, {})
    stats = c.setdefault("futbol_tahmin_stats", {})
    kazanc_config = c.get("futbol_kazanc", {})
    odul_1x2 = kazanc_config.get("1X2", 100)
    odul_skor = kazanc_config.get("skor", 300)

    kazananlar, yanlilar = [], []
    for uid, t_raw in tahminler.items():
        t_sec = t_raw.split("|")[0]
        t_tip = t_raw.split("|")[1] if "|" in t_raw else "1X2"
        uye_stats = stats.setdefault(uid, {"dogru":0,"yanlis":0,"toplam_puan":0})
        isim = c.get("bakiyeler",{}).get(uid,{}).get("isim","?")
        dogru = _tahmin_dogru_mu(t_raw, skor, m)
        if dogru:
            odul = odul_skor if t_tip == "skor" else odul_1x2
            add_puan(c, uid, isim, odul)
            uye_stats["dogru"] += 1
            uye_stats["toplam_puan"] += odul
            kazananlar.append(f"✅ {isim} (+{odul}p)")
            # 3 üst üste doğru bonusu
            seri_dogru = uye_stats.get("seri_dogru", 0) + 1
            uye_stats["seri_dogru"] = seri_dogru
            if seri_dogru >= 3:
                ekstra = kazanc_config.get("galibiyet_serisi", 50)
                add_puan(c, uid, isim, ekstra)
                uye_stats["toplam_puan"] += ekstra
                kazananlar[-1] += f" 🔥+{ekstra}p seri bonusu"
                uye_stats["seri_dogru"] = 0
        else:
            uye_stats["yanlis"] += 1
            uye_stats["seri_dogru"] = 0
            yanlilar.append(isim)

        # DM bildir
        try:
            sonuc_msg = (
                f"⚽ <b>Maç Sonuçlandı!</b>\n\n"
                f"{m.get('ev','?')} <b>{skor}</b> {m.get('deplasman','?')}\n"
                f"Tahminin: <b>{t_sec}</b>\n"
            )
            if dogru:
                odul2 = odul_skor if t_tip == "skor" else odul_1x2
                sonuc_msg += f"✅ <b>DOĞRU! +{odul2} puan kazandın!</b>"
            else:
                sonuc_msg += f"❌ Yanlış. Doğru: {gercek_1x2} ({skor})"
            await context.bot.send_message(int(uid), sonuc_msg, parse_mode="HTML")
        except: pass

    save(c)

    # Admin özeti
    le = lig_emoji(m.get("lig",""))
    ozet = (
        f"✅ <b>Maç Sonuçlandı!</b>\n\n"
        f"{le} {m.get('lig','')}\n"
        f"🏠 {m.get('ev','?')}  <b>{skor}</b>  🚌 {m.get('deplasman','?')}\n"
        f"Sonuç: {'🏠 Ev' if gercek_1x2=='1' else ('🤝 Beraberlik' if gercek_1x2=='X' else '🚌 Deplasman')}\n\n"
        f"📊 Tahminler:\n"
        f"✅ Doğru: {len(kazananlar)} kişi\n"
        f"❌ Yanlış: {len(yanlilar)} kişi\n"
        f"Toplam: {len(tahminler)}\n\n"
    )
    if kazananlar:
        ozet += "<b>Kazananlar:</b>\n" + "\n".join(kazananlar[:10])
    await update.message.reply_text(ozet, parse_mode="HTML")

    # Kanal duyurusu
    for kanal in c.get("kanallar", []):
        kid = kanal.split("|")[0].strip()
        try:
            await context.bot.send_message(
                kid,
                f"⚽ <b>MAÇ SONUCU</b>\n\n"
                f"{le} {m.get('lig','')}\n"
                f"🏠 <b>{m.get('ev','?')}</b>  {skor}  <b>{m.get('deplasman','?')}</b> 🚌\n\n"
                f"🏆 {len(kazananlar)} kişi doğru tahmin yaptı!\n"
                f"📊 Liderlik: /tahmin_top",
                parse_mode="HTML"
            )
        except: pass


async def mac_iptal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: /mac_iptal [MAC_ID]"""
    if not is_admin(update.effective_user.id): return
    if not context.args:
        return await auto_reply(update, "Kullanım: /mac_iptal [MAC_ID]")
    mid = context.args[0].upper()
    c = cfg()
    if mid not in c.get("futbol_maclar", {}):
        return await auto_reply(update, f"❌ [{mid}] bulunamadı.")
    c["futbol_maclar"][mid]["durum"] = "iptal"
    save(c)
    await update.message.reply_text(f"❌ [{mid}] iptal edildi. Tahminler iade edilmez.")


# ─────────────────────────────────────────
# INLINE BUTON CALLBACK (maç seçimi)
# ─────────────────────────────────────────

async def mac_tahmin_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maç listesinden tıklanınca tahmin seçenekleri göster"""
    query = update.callback_query
    await query.answer()
    data = query.data  # mac_sec_ABCDEF

    if data.startswith("mac_sec_"):
        mid = data.replace("mac_sec_","")
        c = cfg()
        m = c.get("futbol_maclar",{}).get(mid,{})
        if not m:
            return await query.edit_message_text("❌ Maç bulunamadı.")
        if m.get("durum") != "bekliyor":
            return await query.edit_message_text("❌ Bu maç için tahmin yapılamaz.")
        le = lig_emoji(m.get("lig",""))
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"🏠 {m.get('ev','?')[:15]} (1)", callback_data=f"mac_tahmin_{mid}_1"),
                InlineKeyboardButton("🤝 Beraberlik (X)", callback_data=f"mac_tahmin_{mid}_X"),
                InlineKeyboardButton(f"🚌 {m.get('deplasman','?')[:15]} (2)", callback_data=f"mac_tahmin_{mid}_2"),
            ],
            [InlineKeyboardButton("◀️ Geri", callback_data="mac_geri")]
        ])
        await query.edit_message_text(
            f"⚽ <b>Tahmin Yap</b>\n\n"
            f"{le} {m.get('lig','')}\n"
            f"🏠 <b>{m.get('ev','?')}</b>  vs  <b>{m.get('deplasman','?')}</b> 🚌\n"
            f"🕐 {m.get('tarih','')[:16]}\n\n"
            f"Sonucu tahmin et:",
            parse_mode="HTML",
            reply_markup=kb
        )

    elif data.startswith("mac_tahmin_"):
        # mac_tahmin_ABCDEF_1
        parca = data.split("_")
        mid = parca[2]
        secim = parca[3]
        c = cfg()
        uid = str(query.from_user.id)
        isim = query.from_user.first_name
        m = c.get("futbol_maclar",{}).get(mid,{})
        if not m or m.get("durum") != "bekliyor":
            return await query.edit_message_text("❌ Bu maç için tahmin yapılamaz.")
        tahminler = c.setdefault("futbol_tahminler",{})
        tahminler.setdefault(mid,{})[uid] = f"{secim}|1X2"
        save(c)
        odul = c.get("futbol_kazanc",{}).get("1X2",100)
        label = {"1":f"🏠 {m.get('ev','?')} kazanır","X":"🤝 Beraberlik","2":f"🚌 {m.get('deplasman','?')} kazanır"}
        await query.edit_message_text(
            f"✅ <b>Tahmin Kaydedildi!</b>\n\n"
            f"⚽ {m.get('ev','?')} vs {m.get('deplasman','?')}\n"
            f"📌 Tahminин: <b>{label.get(secim,secim)}</b>\n"
            f"🏆 Doğru olursa: <b>+{odul} puan</b>\n\n"
            f"📊 /tahminlerim | 🏆 /tahmin_top",
            parse_mode="HTML"
        )

    elif data == "mac_geri":
        await query.edit_message_text("⚽ /maclar ile maç listesine bak!")


def _tahmin_dogru_mu(t_raw, skor, m):
    """Tahminin doğru olup olmadığını kontrol et"""
    t_sec = t_raw.split("|")[0]
    t_tip = t_raw.split("|")[1] if "|" in t_raw else "1X2"
    try:
        ev_g, dep_g = int(skor.split("-")[0]), int(skor.split("-")[1])
    except:
        return False
    if t_tip == "skor":
        return t_sec == skor
    else:
        if ev_g > dep_g: gercek = "1"
        elif ev_g == dep_g: gercek = "X"
        else: gercek = "2"
        return t_sec == gercek



async def anket_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not context.args: return await auto_reply(update, "Kullanım: /anket Soru?|Seçenek1|Seçenek2|Seçenek3")
    parcalar=" ".join(context.args).split("|")
    if len(parcalar)<3: return await auto_reply(update, "❌ En az 2 seçenek lazım!")
    soru=parcalar[0].strip(); secenekler=[p.strip() for p in parcalar[1:]]
    try:
        await context.bot.send_poll(update.effective_chat.id, soru, secenekler, is_anonymous=False)
    except Exception as e: await update.message.reply_text(f"❌ {e}")

# KRİPTO

async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not update.message.reply_to_message: return await auto_reply(update, "Banlamak için mesajı yanıtla!")
    hedef=update.message.reply_to_message.from_user
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, hedef.id)
        await update.message.reply_text(f"🔨 <b>{hedef.first_name}</b> banlandı!", parse_mode="HTML")
    except Exception as e: await update.message.reply_text(f"❌ {e}")

async def btc_cmd(update, context): context.args=["BTC"]; await kripto_cmd(update, context)

async def butonsil_cmd(update, context):
    if not is_admin(update.effective_user.id): return
    c=cfg()
    if not context.args or not context.args[0].isdigit(): return await auto_reply(update, "Kullanım: /butonsil 1")
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

YETKILER = {
    "ban":        2,
    "kick":       2,
    "mute":       2,
    "warn":       1,
    "casino":     2,
    "bakiye_ver": 3,
    "kanal_ekle": 3,
    "ayarlar":    3,
    "lisans":     3,
}

async def cevap_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if len(context.args)<2: return await auto_reply(update, "Kullanım: /cevap [ticket_id] [mesaj]")
    c=cfg(); tid=context.args[0]; mesaj=" ".join(context.args[1:])
    if tid not in c.get("tickets",{}): return await auto_reply(update, "❌ Ticket bulunamadı!")
    ticket=c["tickets"][tid]; ticket["durum"]="kapali"; save(c)
    try:
        await context.bot.send_message(ticket["user_id"], f"🎫 <b>Ticket #{tid} Yanıtlandı</b>\n\n{mesaj}", parse_mode="HTML")
        await update.message.reply_text("✅ Yanıt gönderildi!")
    except: await update.message.reply_text("❌ Kullanıcıya ulaşılamadı!")

# ÜCRETLI ÜYELİK

async def destek_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await auto_reply(update, "Kullanım: /destek [mesajın]")
    c=cfg(); uid=update.effective_user.id
    tid=str(uid)[-6:]
    c.setdefault("tickets",{})[tid]={"durum":"acik","isim":update.effective_user.first_name,"user_id":uid,"mesaj":" ".join(context.args)}
    save(c)
    await update.message.reply_text(f"🎫 Ticket açıldı #{tid}\nEn kısa sürede yanıtlanacak!")
    for aid in c["adminler"]:
        try: await context.bot.send_message(aid, f"🎫 <b>Yeni Ticket #{tid}</b>\n👤 {update.effective_user.first_name} ({uid})\n💬 {' '.join(context.args)}\n\nCevap: /cevap {tid} [mesaj]", parse_mode="HTML")
        except: pass

async def emojisil_cmd(update, context):
    if not is_admin(update.effective_user.id): return
    c=cfg()
    if not context.args: return await auto_reply(update, "Kullanım: /emojisil kelime")
    k=context.args[0].lower()
    if k in c["emoji_kurallar"]: del c["emoji_kurallar"][k]; save(c); await update.message.reply_text(f"🗑 {k} silindi!")
    else: await update.message.reply_text("❌ Bulunamadı!")

async def eth_cmd(update, context): context.args=["ETH"]; await kripto_cmd(update, context)

async def futbol_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """⚽ Penaltı atışı — Kaleciye karşı şans dene!"""
    c = cfg()
    if not c["casino_aktif"]: return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if len(context.args) < 2:
        return await auto_reply(update, 
            "⚽ Kullanım: /penalti [bahis] [sol|orta|sag]\nKaleci rastgele bir tarafa atlayacak!")
    try:
        bahis = int(context.args[0]); yon = context.args[1].lower()
        if yon not in ["sol","orta","sag","sağ"]:
            return await auto_reply(update, "❌ sol, orta veya sag yaz!")
        b = get_bakiye(c, uid)
        if b["puan"] < bahis: return await auto_reply(update, "❌ Yetersiz bakiye!")
        if bahis < c["casino_min_bahis"] or bahis > c["casino_max_bahis"]:
            return await auto_reply(update, f"❌ {c['casino_min_bahis']}-{c['casino_max_bahis']} arası!")

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

GOREVLER = {
    "ilk_giris":   {"puan": 100, "aciklama": "🎉 İlk girişin", "tekrar": False},
    "profil_foto": {"puan": 50,  "aciklama": "📸 Profil fotoğrafı", "tekrar": False},
    "ilk_oyun":    {"puan": 30,  "aciklama": "🎮 İlk oyununu oynadın", "tekrar": False},
    "gunluk_mesaj":{"puan": 5,   "aciklama": "💬 Günlük mesaj", "tekrar": True},
    "haftalik":    {"puan": 200, "aciklama": "📅 Haftalık giriş", "tekrar": True},
}

async def iptal(update, context, *args): context.user_data["bekle"]=None; await update.message.reply_text("❌ İptal.")

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

async def kick_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not update.message.reply_to_message: return await auto_reply(update, "Kicklemek için mesajı yanıtla!")
    hedef=update.message.reply_to_message.from_user
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, hedef.id)
        await context.bot.unban_chat_member(update.effective_chat.id, hedef.id)
        await update.message.reply_text(f"👟 <b>{hedef.first_name}</b> kicklendi!", parse_mode="HTML")
    except Exception as e: await update.message.reply_text(f"❌ {e}")

def _kripto_id(sembol):
    MAP = {
        "BTC":"bitcoin","ETH":"ethereum","TON":"the-open-network",
        "BNB":"binancecoin","SOL":"solana","USDT":"tether",
        "USDC":"usd-coin","XRP":"ripple","ADA":"cardano",
        "AVAX":"avalanche-2","DOT":"polkadot","MATIC":"matic-network",
        "DOGE":"dogecoin","SHIB":"shiba-inu","TRX":"tron",
        "LTC":"litecoin","LINK":"chainlink","UNI":"uniswap",
        "ATOM":"cosmos","FIL":"filecoin",
    }
    return MAP.get(sembol.upper(), sembol.lower())


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

async def kurallar_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c=cfg()
    await update.message.reply_text(f"📌 <b>Grup Kuralları</b>\n\n{c['kurallar']}", parse_mode="HTML")

async def mute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not update.message.reply_to_message: return await auto_reply(update, "Mutlamak için mesajı yanıtla!")
    hedef=update.message.reply_to_message.from_user
    sure=int(context.args[0]) if context.args else 10
    try:
        until=datetime.now()+timedelta(minutes=sure)
        await context.bot.restrict_chat_member(update.effective_chat.id, hedef.id,
            permissions=ChatPermissions(can_send_messages=False), until_date=until)
        await update.message.reply_text(f"🔇 <b>{hedef.first_name}</b> {sure} dakika susturuldu!", parse_mode="HTML")
    except Exception as e: await update.message.reply_text(f"❌ {e}")

async def onayla_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if len(context.args)<2: return await auto_reply(update, "Kullanım: /onayla [user_id] [1ay|3ay|yillik]")
    c=cfg()
    try:
        uid_str,plan=context.args[0],context.args[1]
        if plan not in c["uyelik_fiyatlar"]: return await auto_reply(update, "❌ Plan: 1ay, 3ay, yillik")
        gun=c["uyelik_fiyatlar"][plan]["gun"]
        bitis=(datetime.now()+timedelta(days=gun)).strftime("%Y-%m-%d")
        c["uyelikler"][uid_str]={"plan":plan,"bitis":bitis,"aktif":True,"isim":f"Kullanıcı {uid_str}"}
        c["stats"]["uyelik_satis"]+=1; save(c)
        await update.message.reply_text(f"✅ Onaylandı! {uid_str} → {plan} → {bitis}")
        try: await context.bot.send_message(int(uid_str), f"✅ Üyeliğin onaylandı!\nPlan: {plan}\nBitiş: {bitis} 🎉")
        except: pass
    except Exception as e: await update.message.reply_text(f"❌ {e}")

async def otosil_cmd(update, context):
    if not is_admin(update.effective_user.id): return
    c=cfg()
    if not context.args or not context.args[0].isdigit(): return await auto_reply(update, "Kullanım: /otosil 2")
    idx=int(context.args[0])-1
    if 0<=idx<len(c["oto_mesajlar"]): c["oto_mesajlar"].pop(idx); save(c); await update.message.reply_text("🗑 Silindi!")
    else: await update.message.reply_text("❌ Geçersiz!")

async def ton_cmd(update, context): context.args=["TON"]; await kripto_cmd(update, context)

# TICKET & DESTEK

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

async def uyeol_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c=cfg()
    if not c["uyelik_aktif"]: return await auto_reply(update, "❌ Üyelik sistemi aktif değil.")
    txt=("💰 <b>Ücretli Üyelik</b>\n\n"
        +"\n".join([f"• {v['label']}: <b>{v['fiyat']} USDT</b>" for v in c['uyelik_fiyatlar'].values()])
        +f"\n\n💎 TON: <code>{c['uyelik_ton_adres']}</code>\n💵 USDT: <code>{c['uyelik_usdt_adres']}</code>\n\nÖdeme sonrası yöneticiye ulaşın.")
    await update.message.reply_text(txt, parse_mode="HTML")

# ── JOIN HANDLER ─────────────────────────────────────────────────

async def warn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not update.message.reply_to_message: return await auto_reply(update, "Uyarmak için mesajı yanıtla!")
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

async def yasakekle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not context.args: return await auto_reply(update, "Kullanım: /yasakekle kelime")
    c=cfg(); kelime=" ".join(context.args).lower()
    if kelime not in c["yasakli_kelimeler"]: c["yasakli_kelimeler"].append(kelime); save(c)
    await update.message.reply_text(f"✅ '{kelime}' yasaklı listeye eklendi!")

async def yasaksil_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not context.args: return await auto_reply(update, "Kullanım: /yasaksil kelime")
    c=cfg(); kelime=" ".join(context.args).lower()
    if kelime in c["yasakli_kelimeler"]: c["yasakli_kelimeler"].remove(kelime); save(c); await update.message.reply_text(f"✅ '{kelime}' kaldırıldı!")
    else: await update.message.reply_text("❌ Bulunamadı!")

# ANKET

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


# ════════════════════════════════════════════════════════════════
#  SOSYAL & TOPLU OYUNLAR
#  1. BİLGİ YARIŞMASI (Quiz)
#  2. DÜELLO (1v1)
#  3. JACKPOT HAVUZU
#  4. KASAYLA BLACKJACK
# ════════════════════════════════════════════════════════════════

import asyncio as _asyncio
import time as _time

# ── VARSAYILAN SORULAR ────────────────────────────────────────
VARSAYILAN_SORULAR = [
    {"s": "Türkiye'nin başkenti neresidir?", "c": ["Ankara","ankara"], "ip": "🏛"},
    {"s": "Kaç tane gezegenimiz var?", "c": ["8","sekiz"], "ip": "🪐"},
    {"s": "Suyun kimyasal formülü nedir?", "c": ["H2O","h2o"], "ip": "💧"},
    {"s": "1 düzine kaç tanedir?", "c": ["12","on iki"], "ip": "🔢"},
    {"s": "Hangi hayvan 'orman kralı' olarak bilinir?", "c": ["aslan","lion"], "ip": "🦁"},
    {"s": "Dünya'nın en büyük okyanusu hangisidir?", "c": ["büyük okyanus","pasifik","pacific"], "ip": "🌊"},
    {"s": "İnsan vücudunda kaç kemik vardır?", "c": ["206"], "ip": "🦴"},
    {"s": "Güneş sistemimizdeki en büyük gezegen hangisidir?", "c": ["jüpiter","jupiter"], "ip": "🪐"},
    {"s": "Elmanın düşmesi hangi bilim insanına esin kaynağı oldu?", "c": ["newton","isaac newton"], "ip": "🍎"},
    {"s": "Bir yılda kaç ay vardır?", "c": ["12","on iki"], "ip": "📅"},
    {"s": "Türkiye kaç kıtada yer alır?", "c": ["2","iki"], "ip": "🌍"},
    {"s": "Hangi metal sıvı hâlde bulunur?", "c": ["cıva","civayı"], "ip": "⚗️"},
    {"s": "Işığın hızı yaklaşık kaç km/s'dir?", "c": ["300000","300.000","299792"], "ip": "💡"},
    {"s": "Piramitler hangi ülkededir?", "c": ["mısır","egypt"], "ip": "🔺"},
    {"s": "Türkiye'nin para birimi nedir?", "c": ["türk lirası","lira","tl"], "ip": "💰"},
    {"s": "Hangi ülke hem kıta hem ülkedir?", "c": ["avustralya","australia"], "ip": "🦘"},
    {"s": "Bal yapan böcek hangisidir?", "c": ["arı","bee"], "ip": "🐝"},
    {"s": "1 saatte kaç dakika vardır?", "c": ["60","altmış"], "ip": "⏰"},
    {"s": "En hızlı kara hayvanı hangisidir?", "c": ["çita","cheetah"], "ip": "🐆"},
    {"s": "Hangi vitamin güneş ışığından üretilir?", "c": ["d","d vitamini","vitamin d"], "ip": "☀️"},
]

# ════════════════════════════════════════════════════════════
# 1. BİLGİ YARIŞMASI
# ════════════════════════════════════════════════════════════

async def quiz_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: /quiz [soru_sayısı] — Bilgi yarışması başlat"""
    c = cfg()
    if not c.get("quiz_aktif", True): return
    if not is_admin(update.effective_user.id):
        return await auto_reply(update, "❌ Sadece adminler quiz başlatabilir!")
    chat_id = str(update.effective_chat.id)
    aktif = c.get("quiz_aktif_oyun", {})
    if chat_id in aktif:
        return await auto_reply(update, "⚠️ Zaten aktif bir quiz var! /quiz_bitir ile durdur.")
    sayi = int(context.args[0]) if context.args and context.args[0].isdigit() else 5
    sayi = max(1, min(20, sayi))
    sorular = c.get("quiz_sorular", []) or VARSAYILAN_SORULAR
    secilen = random.sample(sorular, min(sayi, len(sorular)))
    aktif[chat_id] = {
        "sorular": secilen, "indeks": 0,
        "puan": {},   # {uid: puan}
        "isimler": {},
        "cevaplayan": set(),  # bu soruda kim cevapladı
        "aktif": True,
    }
    c["quiz_aktif_oyun"] = aktif
    save(c)
    sure = c.get("quiz_sure", 20)
    await update.message.reply_text(
        f"🧠 <b>Bilgi Yarışması Başlıyor!</b>\n\n"
        f"📋 {sayi} soru  |  ⏱ Her soru {sure} saniye\n"
        f"🏆 Doğru cevap: +{c.get('quiz_odul',150)} puan\n\n"
        f"Hazır mısınız? İlk soru geliyor...",
        parse_mode="HTML"
    )
    await _asyncio.sleep(3)
    await _quiz_sonraki_soru(context, chat_id, update.effective_chat.id)

async def _quiz_sonraki_soru(context, chat_id_str, chat_id_int):
    c = cfg()
    aktif = c.get("quiz_aktif_oyun", {})
    if chat_id_str not in aktif: return
    oyun = aktif[chat_id_str]
    if not oyun.get("aktif"): return
    idx = oyun["indeks"]
    sorular = oyun["sorular"]
    if idx >= len(sorular):
        await _quiz_bitir(context, chat_id_str, chat_id_int)
        return
    soru = sorular[idx]
    oyun["cevaplayan"] = []
    oyun["indeks"] += 1
    oyun["bitis"] = _time.time() + c.get("quiz_sure", 20)
    c["quiz_aktif_oyun"] = aktif
    save(c)
    sure = c.get("quiz_sure", 20)
    msg = await context.bot.send_message(
        chat_id_int,
        f"🧠 <b>Soru {idx+1}/{len(sorular)}</b> {soru.get('ip','')}\n\n"
        f"❓ {soru['s']}\n\n"
        f"⏱ <b>{sure} saniye</b>",
        parse_mode="HTML"
    )
    # Zamanlayıcı
    await _asyncio.sleep(sure)
    c2 = cfg()
    aktif2 = c2.get("quiz_aktif_oyun", {})
    if chat_id_str not in aktif2 or not aktif2[chat_id_str].get("aktif"): return
    oyun2 = aktif2[chat_id_str]
    if oyun2["indeks"] == idx + 1:  # hâlâ aynı soruda
        await context.bot.send_message(
            chat_id_int,
            f"⏰ Süre doldu! Cevap: <b>{soru['c'][0].upper()}</b>",
            parse_mode="HTML"
        )
        await _asyncio.sleep(2)
        await _quiz_sonraki_soru(context, chat_id_str, chat_id_int)

async def quiz_mesaj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quiz aktifken gelen mesajları kontrol et"""
    c = cfg()
    chat_id = str(update.effective_chat.id)
    aktif = c.get("quiz_aktif_oyun", {})
    if chat_id not in aktif: return
    oyun = aktif[chat_id]
    if not oyun.get("aktif"): return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    idx = oyun["indeks"] - 1
    if idx < 0 or idx >= len(oyun["sorular"]): return
    soru = oyun["sorular"][idx]
    if uid in oyun.get("cevaplayan", []):
        return  # zaten cevapladı
    metin = (update.message.text or "").strip().lower()
    dogru_cevaplar = [c2.lower() for c2 in soru["c"]]
    if metin in dogru_cevaplar:
        odul = c.get("quiz_odul", 150)
        oyun.setdefault("puan", {})[uid] = oyun["puan"].get(uid, 0) + odul
        oyun.setdefault("isimler", {})[uid] = isim
        oyun.setdefault("cevaplayan", []).append(uid)
        add_puan(c, uid, isim, odul)
        c["quiz_aktif_oyun"] = aktif
        save(c)
        await update.message.reply_text(
            f"✅ <b>{isim}</b> doğru! +{odul} puan 🎉",
            parse_mode="HTML"
        )
        await _asyncio.sleep(2)
        await _quiz_sonraki_soru(context, chat_id, update.effective_chat.id)

async def _quiz_bitir(context, chat_id_str, chat_id_int):
    c = cfg()
    aktif = c.get("quiz_aktif_oyun", {})
    oyun = aktif.get(chat_id_str, {})
    if not oyun: return
    puan = oyun.get("puan", {})
    isimler = oyun.get("isimler", {})
    del aktif[chat_id_str]
    c["quiz_aktif_oyun"] = aktif
    save(c)
    if not puan:
        await context.bot.send_message(chat_id_int,
            "🧠 Quiz bitti! Kimse doğru cevap veremedi. 😢")
        return
    sirali = sorted(puan.items(), key=lambda x: x[1], reverse=True)
    madalya = ["🥇","🥈","🥉"]
    metin = "🧠 <b>Quiz Bitti! Sonuçlar:</b>\n\n"
    for i, (uid, p) in enumerate(sirali[:10]):
        icon = madalya[i] if i < 3 else f"{i+1}."
        metin += f"{icon} {isimler.get(uid,'?')} — <b>{p} puan</b>\n"
    await context.bot.send_message(chat_id_int, metin, parse_mode="HTML")

async def quiz_bitir_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: /quiz_bitir — Quiz'i durdur"""
    if not is_admin(update.effective_user.id): return
    c = cfg()
    chat_id = str(update.effective_chat.id)
    aktif = c.get("quiz_aktif_oyun", {})
    if chat_id not in aktif:
        return await auto_reply(update, "Aktif quiz yok.")
    aktif[chat_id]["aktif"] = False
    c["quiz_aktif_oyun"] = aktif
    save(c)
    await update.message.reply_text("⏹ Quiz durduruldu.")

async def quiz_soru_ekle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: /quiz_ekle [soru] | [cevap1,cevap2]"""
    if not is_admin(update.effective_user.id): return
    if not context.args:
        return await auto_reply(update, 
            "Kullanım: /quiz_ekle Soru metni | cevap1,cevap2\n"
            "Örnek: /quiz_ekle Türkiye'nin başkenti? | Ankara,ankara")
    metin = " ".join(context.args)
    if "|" not in metin:
        return await auto_reply(update, "❌ | ile soru ve cevabı ayır!")
    parca = metin.split("|", 1)
    soru_m = parca[0].strip()
    cevaplar = [c2.strip() for c2 in parca[1].split(",")]
    c = cfg()
    c.setdefault("quiz_sorular", []).append({"s": soru_m, "c": cevaplar, "ip": "❓"})
    save(c)
    await update.message.reply_text(
        f"✅ Soru eklendi!\n❓ {soru_m}\n✅ Cevaplar: {', '.join(cevaplar)}\n"
        f"Toplam soru: {len(c['quiz_sorular'])}")

# ════════════════════════════════════════════════════════════
# 2. DÜELLO (1v1)
# ════════════════════════════════════════════════════════════

async def duello_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """⚔️ /duello @kullanici [bahis] — 1v1 meydan okuma"""
    c = cfg()
    if not c.get("duello_aktif", True): return
    if not c.get("bakiye_aktif"): return
    if not context.args or len(context.args) < 2:
        return await auto_reply(update, 
            "⚔️ <b>Düello</b>\n\nKullanım: /duello @kullanici [bahis]\n"
            "Örnek: /duello @ahmet 500\n\n"
            "Kazanan tüm bahisi alır! 🏆", parse_mode="HTML")
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    hata, bahis = bahis_kontrol(c, uid, context.args[-1])
    if hata: return await auto_reply(update, hata)
    # Rakip mention'ı
    rakip_mention = context.args[0].replace("@","")
    duello_id = f"D{random.randint(10000,99999)}"
    c.setdefault("duello_bekleyen", {})[duello_id] = {
        "meydan_okuyan_id": uid,
        "meydan_okuyan_isim": isim,
        "rakip_mention": rakip_mention,
        "bahis": bahis,
        "zaman": _time.time(),
        "chat_id": update.effective_chat.id,
    }
    save(c)
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("⚔️ Kabul Et", callback_data=f"duello_kabul_{duello_id}"),
        InlineKeyboardButton("❌ Reddet",   callback_data=f"duello_red_{duello_id}"),
    ]])
    await update.message.reply_text(
        f"⚔️ <b>DÜELLO MEYDAN OKUMASI!</b>\n\n"
        f"🗡 <b>{isim}</b> → @{rakip_mention}\n"
        f"💰 Bahis: <b>{bahis:,} puan</b>\n\n"
        f"@{rakip_mention}, meydan okumayı kabul ediyor musun?\n"
        f"⏳ 60 saniye içinde yanıtla!",
        parse_mode="HTML", reply_markup=kb)

async def duello_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    uid = str(query.from_user.id)
    isim = query.from_user.first_name
    c = cfg()
    if data.startswith("duello_kabul_"):
        duello_id = data.replace("duello_kabul_","")
        bekleyen = c.get("duello_bekleyen",{})
        if duello_id not in bekleyen:
            return await query.edit_message_text("❌ Düello süresi doldu veya iptal edildi.")
        d = bekleyen[duello_id]
        # Süre kontrolü
        if _time.time() - d["zaman"] > 60:
            del bekleyen[duello_id]; save(c)
            return await query.edit_message_text("⏰ Düello süresi doldu!")
        # Bakiye kontrol
        hata_r, _ = bahis_kontrol(c, uid, str(d["bahis"]))
        if hata_r:
            return await query.edit_message_text(f"❌ {isim} yeterli bakiyesi yok: {hata_r}")
        # DÜELLO OYNANİYOR — Zar ile
        meydan_uid = d["meydan_okuyan_id"]
        meydan_isim = d["meydan_okuyan_isim"]
        bahis = d["bahis"]
        zar1 = random.randint(1,6); zar2 = random.randint(1,6)
        ze = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣"]
        while zar1 == zar2:  # beraberlik olmasın
            zar1 = random.randint(1,6); zar2 = random.randint(1,6)
        if zar1 > zar2:
            kazanan_uid, kazanan_isim = meydan_uid, meydan_isim
            kaybeden_uid, kaybeden_isim = uid, isim
            k1, k2 = zar1, zar2
        else:
            kazanan_uid, kazanan_isim = uid, isim
            kaybeden_uid, kaybeden_isim = meydan_uid, meydan_isim
            k1, k2 = zar2, zar1
        add_puan(c, kazanan_uid, kazanan_isim, bahis)
        add_puan(c, kaybeden_uid, kaybeden_isim, -bahis)
        del bekleyen[duello_id]
        c["duello_bekleyen"] = bekleyen
        save(c)
        SENARYOLAR_D = [
            "🎲 Zarlar konuştu! {k1} vs {k2} — {kazan} zaferi kucakladı!",
            "⚔️ Epik kapışma! {kazan} {k1} ile {kaybet} {k2}\'yi devirdi!",
            "🏆 Şampiyon belli oldu! {kazan} {k1} > {kaybet} {k2}",
            "🔥 {kazan} ateş topladı! {k1} vs {k2} — Zafer {kazan}\'ın!",
        ]
        senaryo = random.choice(SENARYOLAR_D).format(
            kazan=kazanan_isim, kaybet=kaybeden_isim,
            k1=ze[zar1-1], k2=ze[zar2-1])
        sonuc = await query.edit_message_text(
            f"⚔️ <b>DÜELLO SONUCU!</b>\n\n"
            f"{senaryo}\n\n"
            f"👑 <b>{kazanan_isim} +{bahis:,} puan</b>\n"
            f"💸 {kaybeden_isim} -{bahis:,} puan",
            parse_mode="HTML")
    elif data.startswith("duello_red_"):
        duello_id = data.replace("duello_red_","")
        bekleyen = c.get("duello_bekleyen",{})
        if duello_id in bekleyen:
            d = bekleyen[duello_id]
            del bekleyen[duello_id]; save(c)
            await query.edit_message_text(
                f"❌ <b>{isim}</b> düelloyu reddetti.",
                parse_mode="HTML")

# ════════════════════════════════════════════════════════════
# 3. JACKPOT HAVUZU
# ════════════════════════════════════════════════════════════

def jackpot_katki_kes(c, uid, isim, bahis):
    """Casino oyunlarından %katki jackpot'a aktar"""
    oran = c.get("jackpot_katki", 2) / 100
    katki = max(1, int(bahis * oran))
    c["jackpot_havuz"] = c.get("jackpot_havuz", 0) + katki
    return katki

async def jackpot_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """💰 /jackpot — Jackpot havuzunu gör ve katıl"""
    c = cfg()
    if not c.get("jackpot_aktif", True): return
    havuz = c.get("jackpot_havuz", 0)
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    chat_id = str(update.effective_chat.id)
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton(f"🎰 Çekilişe Katıl!", callback_data=f"jackpot_katil_{chat_id}")
    ]])
    await update.message.reply_text(
        f"💰 <b>JACKPOT HAVUZU</b>\n\n"
        f"🏆 Mevcut Havuz: <b>{havuz:,} puan</b>\n\n"
        f"Her casino oyunundan %{c.get('jackpot_katki',2)} bu havuza eklenir.\n"
        f"Admin çekiliş başlatınca katılabilirsin!\n\n"
        f"🎰 Çekilişe katılmak için butona bas:",
        parse_mode="HTML", reply_markup=kb)

async def jackpot_cekilis_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: /jackpot_cekilis — Jackpot çekilişi başlat"""
    if not is_admin(update.effective_user.id): return
    c = cfg()
    havuz = c.get("jackpot_havuz", 0)
    if havuz < 100:
        return await auto_reply(update, f"❌ Havuz çok az: {havuz} puan. Min 100 gerekli.")
    chat_id = str(update.effective_chat.id)
    # Katılımcıları temizle ve başlat
    c.setdefault("jackpot_son", {})[chat_id] = {
        "katilimcilar": {},
        "baslangic": _time.time(),
        "havuz": havuz,
        "aktif": True,
    }
    save(c)
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("🎰 Katıl!", callback_data=f"jackpot_katil_{chat_id}")
    ]])
    msg = await update.message.reply_text(
        f"🎰 <b>JACKPOT ÇEKİLİŞİ BAŞLADI!</b>\n\n"
        f"💰 Havuz: <b>{havuz:,} puan</b>\n"
        f"⏳ 60 saniye içinde katıl!\n\n"
        f"👇 Butona bas ve şansını dene!",
        parse_mode="HTML", reply_markup=kb)
    await _asyncio.sleep(60)
    c2 = cfg()
    jdata = c2.get("jackpot_son",{}).get(chat_id,{})
    if not jdata.get("aktif"): return
    katilimcilar = jdata.get("katilimcilar",{})
    jdata["aktif"] = False
    c2["jackpot_son"][chat_id] = jdata
    if not katilimcilar:
        save(c2)
        await context.bot.send_message(update.effective_chat.id,
            "😢 Jackpot çekilişine kimse katılmadı! Havuz birikmeye devam ediyor.")
        return
    kazanan_uid = random.choice(list(katilimcilar.keys()))
    kazanan_isim = katilimcilar[kazanan_uid]
    add_puan(c2, kazanan_uid, kazanan_isim, havuz)
    c2["jackpot_havuz"] = 0
    save(c2)
    await context.bot.send_message(
        update.effective_chat.id,
        f"🎰 <b>JACKPOT KAZANANI!</b>\n\n"
        f"👑 <b>{kazanan_isim}</b>\n"
        f"💰 <b>+{havuz:,} puan</b> kazandı!\n\n"
        f"🎊 Tebrikler! Havuz sıfırlandı.",
        parse_mode="HTML")

async def jackpot_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if not data.startswith("jackpot_katil_"): return
    chat_id = data.replace("jackpot_katil_","")
    uid = str(query.from_user.id)
    isim = query.from_user.first_name
    c = cfg()
    jdata = c.get("jackpot_son",{}).get(chat_id,{})
    if not jdata.get("aktif"):
        return await query.answer("❌ Aktif çekiliş yok!", show_alert=True)
    katilimcilar = jdata.setdefault("katilimcilar",{})
    if uid in katilimcilar:
        return await query.answer("✅ Zaten katıldın!", show_alert=True)
    katilimcilar[uid] = isim
    c["jackpot_son"][chat_id] = jdata
    save(c)
    sayi = len(katilimcilar)
    await query.answer(f"✅ Katıldın! Toplam {sayi} kişi.", show_alert=True)
    try:
        await query.edit_message_text(
            query.message.text + f"\n👥 Katılımcı: {sayi}",
            parse_mode="HTML",
            reply_markup=query.message.reply_markup)
    except: pass

# ════════════════════════════════════════════════════════════
# 4. KASAYLA BLACKJACK (Canlı masa)
# ════════════════════════════════════════════════════════════

_KBJ_KARTLAR = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"] * 4
_KBJ_DEGER   = {"A":11,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"10":10,"J":10,"Q":10,"K":10}

def _kbj_puan(el):
    p = sum(_KBJ_DEGER[k] for k in el)
    aslar = el.count("A")
    while p > 21 and aslar:
        p -= 10; aslar -= 1
    return p

def _kbj_el_str(el, gizli=False):
    if gizli and len(el) > 1:
        return f"{el[0]} 🂠"
    return " ".join(el) + f" ({_kbj_puan(el)})"

async def kbj_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🃏 /bj [bahis] — Kasayla BlackJack oyna"""
    c = cfg()
    if not c.get("kbj_aktif", True): return
    if not c.get("bakiye_aktif"): return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    if not context.args:
        return await auto_reply(update, 
            "🃏 <b>Kasayla BlackJack</b>\n\nKullanım: /bj [bahis]\n"
            "Örnek: /bj 200\n\n"
            "Hedef: 21'i geçmeden kasadan yüksek puan al!\n"
            "• Kart çek: Kart Al\n• Dur: Dur (kasa devam eder)", parse_mode="HTML")
    hata, bahis = bahis_kontrol(c, uid, context.args[0])
    if hata: return await auto_reply(update, hata)
    # Masa oluştur
    deste = _KBJ_KARTLAR.copy()
    random.shuffle(deste)
    oyuncu_el = [deste.pop(), deste.pop()]
    kasa_el   = [deste.pop(), deste.pop()]
    oyuncu_p  = _kbj_puan(oyuncu_el)
    masalar = c.setdefault("kbj_masalar", {})
    masalar[uid] = {
        "oyuncu_el": oyuncu_el, "kasa_el": kasa_el,
        "deste": deste, "bahis": bahis,
        "isim": isim, "bitti": False,
    }
    save(c)
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("🃏 Kart Al", callback_data=f"kbj_al_{uid}"),
        InlineKeyboardButton("✋ Dur",     callback_data=f"kbj_dur_{uid}"),
    ]])
    await update.message.reply_text(
        f"🃏 <b>BlackJack — {isim}</b>\n\n"
        f"Sen:  {_kbj_el_str(oyuncu_el)}\n"
        f"Kasa: {_kbj_el_str(kasa_el, gizli=True)}\n\n"
        f"💰 Bahis: {bahis:,} puan"
        + ("\n\n🎉 <b>BLACKJACK!</b>" if oyuncu_p==21 else ""),
        parse_mode="HTML",
        reply_markup=None if oyuncu_p==21 else kb)
    if oyuncu_p == 21:
        await _kbj_bitir(update, context, uid, "dur")

async def kbj_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    hedef_uid = data.split("_")[-1]
    uid = str(query.from_user.id)
    if uid != hedef_uid:
        return await query.answer("❌ Bu masa sana ait değil!", show_alert=True)
    c = cfg()
    masalar = c.get("kbj_masalar", {})
    if uid not in masalar or masalar[uid]["bitti"]:
        return await query.edit_message_text("❌ Aktif masa yok.")
    masa = masalar[uid]
    if data.startswith("kbj_al_"):
        # Kart çek
        masa["oyuncu_el"].append(masa["deste"].pop())
        p = _kbj_puan(masa["oyuncu_el"])
        c["kbj_masalar"] = masalar
        save(c)
        if p > 21:
            await query.edit_message_text(
                f"🃏 <b>BlackJack — {masa['isim']}</b>\n\n"
                f"Sen:  {_kbj_el_str(masa['oyuncu_el'])}\n"
                f"Kasa: {_kbj_el_str(masa['kasa_el'], gizli=True)}\n\n"
                f"💥 <b>BUST! 21'i geçtin!</b>",
                parse_mode="HTML")
            await _kbj_bitir_edit(query, context, uid, "bust")
        else:
            kb = InlineKeyboardMarkup([[
                InlineKeyboardButton("🃏 Kart Al", callback_data=f"kbj_al_{uid}"),
                InlineKeyboardButton("✋ Dur",     callback_data=f"kbj_dur_{uid}"),
            ]])
            await query.edit_message_text(
                f"🃏 <b>BlackJack — {masa['isim']}</b>\n\n"
                f"Sen:  {_kbj_el_str(masa['oyuncu_el'])}\n"
                f"Kasa: {_kbj_el_str(masa['kasa_el'], gizli=True)}\n\n"
                f"💰 Bahis: {masa['bahis']:,} puan",
                parse_mode="HTML", reply_markup=kb)
    elif data.startswith("kbj_dur_"):
        await _kbj_bitir_edit(query, context, uid, "dur")

async def _kbj_bitir_edit(query, context, uid, sebep):
    c = cfg()
    masalar = c.get("kbj_masalar", {})
    if uid not in masalar: return
    masa = masalar[uid]
    if masa["bitti"]: return
    masa["bitti"] = True
    isim = masa["isim"]
    bahis = masa["bahis"]
    oyuncu_el = masa["oyuncu_el"]
    kasa_el   = masa["kasa_el"]
    deste     = masa["deste"]
    # Kasa devam eder
    while _kbj_puan(kasa_el) < 17 and deste:
        kasa_el.append(deste.pop())
    o_p = _kbj_puan(oyuncu_el)
    k_p = _kbj_puan(kasa_el)
    if sebep == "bust":
        kazanc = -bahis; sonuc = "💥 Bust! Kaybettin."
    elif o_p == 21 and len(oyuncu_el)==2:
        kazanc = int(bahis*1.5); sonuc = "🃏 BLACKJACK! 1.5x!"
    elif k_p > 21 or o_p > k_p:
        kazanc = bahis; sonuc = "🎉 Kazandın!"
    elif o_p == k_p:
        kazanc = 0; sonuc = "🤝 Beraberlik!"
    else:
        kazanc = -bahis; sonuc = "😢 Kaybettin."
    yeni = add_puan(c, uid, isim, kazanc)
    c["kbj_masalar"] = masalar
    save(c)
    try:
        await query.edit_message_text(
            f"🃏 <b>BlackJack — {isim}</b>\n\n"
            f"Sen:  {_kbj_el_str(oyuncu_el)}\n"
            f"Kasa: {_kbj_el_str(kasa_el)}\n\n"
            f"{sonuc}\n"
            f"{'➕' if kazanc>=0 else '➖'} <b>{abs(kazanc):,} puan</b>\n"
            f"💰 Bakiye: <b>{yeni:,}</b>",
            parse_mode="HTML")
    except: pass

async def _kbj_bitir(update, context, uid, sebep):
    """İlk mesajdan bitir (blackjack anında)"""
    c = cfg()
    masalar = c.get("kbj_masalar", {})
    if uid not in masalar: return
    masa = masalar[uid]
    if masa["bitti"]: return
    masa["bitti"] = True
    isim = masa["isim"]; bahis = masa["bahis"]
    oyuncu_el = masa["oyuncu_el"]; kasa_el = masa["kasa_el"]
    deste = masa["deste"]
    while _kbj_puan(kasa_el) < 17 and deste:
        kasa_el.append(deste.pop())
    o_p = _kbj_puan(oyuncu_el); k_p = _kbj_puan(kasa_el)
    kazanc = int(bahis*1.5); sonuc = "🃏 BLACKJACK! 1.5x!"
    yeni = add_puan(c, uid, isim, kazanc)
    c["kbj_masalar"] = masalar; save(c)
    await update.message.reply_text(
        f"🃏 <b>BlackJack — {isim}</b>\n\n"
        f"Sen:  {_kbj_el_str(oyuncu_el)}\n"
        f"Kasa: {_kbj_el_str(kasa_el)}\n\n"
        f"{sonuc}\n➕ <b>{kazanc:,} puan</b>\n💰 Bakiye: <b>{yeni:,}</b>",
        parse_mode="HTML")



# ═══════════════════════════════════════════════════════════════
#  EKSİK ÖZELLİKLER MODÜLÜ
#  - /temizle  — Mesaj silme
#  - /istat    — Bot istatistikleri
#  - /cekilis  — Çekiliş sistemi
#  - /vip      — VIP bilgi & aktifleştir
#  - /bildirim — DM bildirimleri aç/kapat
#  - /kelime   — Kelime oyunu (zincirleme)
#  - Flood kontrol (mesaj_handler_v2'ye entegre)
#  - Günlük istatistik job
# ═══════════════════════════════════════════════════════════════

# ── /temizle ──────────────────────────────────────────────────
async def temizle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: /temizle [N] — Son N mesajı sil (max 100)"""
    if not is_admin(update.effective_user.id): return
    n = int(context.args[0]) if context.args and context.args[0].isdigit() else 10
    n = min(n, 100)
    try:
        msgs = []
        async for msg in context.bot.get_updates():
            pass
        deleted = await update.effective_chat.delete_messages(
            [update.message.message_id - i for i in range(1, n+1)]
        )
        await update.message.reply_text(f"🗑 {n} mesaj silindi.", parse_mode="HTML")
    except Exception as e:
        # Alternatif yöntem
        try:
            await update.message.delete()
            silinebilir = 0
            for i in range(1, n+1):
                try:
                    await context.bot.delete_message(
                        update.effective_chat.id,
                        update.message.message_id - i
                    )
                    silinebilir += 1
                except: pass
            note = await update.message.reply_text(f"🗑 {silinebilir} mesaj silindi.")
            await _asyncio.sleep(3)
            try: await note.delete()
            except: pass
        except Exception as e2:
            await update.message.reply_text(f"❌ Silme hatası: {e2}")

# ── /istat ────────────────────────────────────────────────────
async def istatistik_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📊 /istat — Bot & grup istatistikleri"""
    c = cfg()
    stats = c.get("stats", {})
    bakiyeler = c.get("bakiyeler", {})
    maclar = c.get("futbol_maclar", {})
    quiz_oyunlar = c.get("quiz_aktif_oyun", {})

    toplam_uye = len(bakiyeler)
    toplam_puan = sum(v.get("bakiye", 0) for v in bakiyeler.values() if isinstance(v, dict))
    casino_oyun = stats.get("casino_oyun", 0)
    aktif_duello = len(c.get("duello_bekleyen", {}))
    jackpot_havuz = c.get("jackpot_havuz", 0)
    toplam_mac = len(maclar)
    tahmin_sayisi = sum(len(v) for v in c.get("futbol_tahminler", {}).values())

    # En zengin 3
    sirali = sorted([(uid, v.get("bakiye",0), v.get("isim","?"))
                     for uid,v in bakiyeler.items() if isinstance(v,dict)],
                    key=lambda x: x[1], reverse=True)[:3]
    zengin_str = "\n".join([f"  {['🥇','🥈','🥉'][i]} {isim}: {b:,}p"
                            for i,(uid,b,isim) in enumerate(sirali)])

    await update.message.reply_text(
        f"📊 <b>SOGTİLLA İstatistikleri</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Kayıtlı üye: <b>{toplam_uye}</b>\n"
        f"💰 Toplam puan: <b>{toplam_puan:,}</b>\n"
        f"🎰 Casino oyunu: <b>{casino_oyun:,}</b>\n"
        f"⚔️ Aktif düello: <b>{aktif_duello}</b>\n"
        f"💎 Jackpot havuz: <b>{jackpot_havuz:,}</b>\n"
        f"⚽ Maç sayısı: <b>{toplam_mac}</b>\n"
        f"🎯 Tahmin sayısı: <b>{tahmin_sayisi}</b>\n\n"
        f"🏆 <b>En Zenginler:</b>\n{zengin_str or '  Henüz kimse yok'}",
        parse_mode="HTML"
    )

# ── /cekilis ──────────────────────────────────────────────────
async def cekilis_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: /cekilis [ödül_puan] [kazanan_sayısı] — Çekiliş başlat"""
    if not is_admin(update.effective_user.id): return
    if not context.args:
        return await auto_reply(update, 
            "🎁 <b>Çekiliş</b>\n\n"
            "Kullanım: /cekilis [ödül] [kazanan_sayısı]\n"
            "Örnek: /cekilis 1000 3\n\n"
            "Üyeler butona basarak katılır, 60sn sonra çekiliş yapılır.",
            parse_mode="HTML")
    odul = int(context.args[0]) if context.args[0].isdigit() else 500
    kazanan_n = int(context.args[1]) if len(context.args) > 1 and context.args[1].isdigit() else 1
    chat_id = str(update.effective_chat.id)
    c = cfg()
    c.setdefault("cekilisler", {})[chat_id] = {
        "odul": odul, "kazanan_n": kazanan_n,
        "katilimcilar": {}, "aktif": True,
        "baslatan": update.effective_user.first_name,
    }
    save(c)
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("🎁 Katıl!", callback_data=f"cekilis_katil_{chat_id}")
    ]])
    msg = await update.message.reply_text(
        f"🎁 <b>ÇEKİLİŞ BAŞLADI!</b>\n\n"
        f"🏆 Ödül: <b>{odul:,} puan</b> × {kazanan_n} kazanan\n"
        f"⏳ 60 saniye içinde katıl!\n"
        f"👇 Butona bas:",
        parse_mode="HTML", reply_markup=kb)
    await _asyncio.sleep(60)
    c2 = cfg()
    cdata = c2.get("cekilisler", {}).get(chat_id, {})
    if not cdata.get("aktif"): return
    cdata["aktif"] = False
    c2["cekilisler"][chat_id] = cdata
    katilimcilar = cdata.get("katilimcilar", {})
    if not katilimcilar:
        save(c2)
        await context.bot.send_message(update.effective_chat.id,
            "😢 Çekilişe kimse katılmadı!")
        return
    k_list = list(katilimcilar.items())
    kazananlar = random.sample(k_list, min(kazanan_n, len(k_list)))
    for uid, isim in kazananlar:
        add_puan(c2, uid, isim, odul)
    save(c2)
    kazanan_str = "\n".join([f"🎉 <b>{isim}</b> +{odul:,} puan" for uid,isim in kazananlar])
    await context.bot.send_message(
        update.effective_chat.id,
        f"🎁 <b>ÇEKİLİŞ SONUÇLANDI!</b>\n\n"
        f"👥 Katılımcı: {len(katilimcilar)}\n\n"
        f"🏆 <b>Kazananlar:</b>\n{kazanan_str}",
        parse_mode="HTML")

async def cekilis_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data.startswith("cekilis_katil_"): return
    chat_id = query.data.replace("cekilis_katil_", "")
    uid = str(query.from_user.id)
    isim = query.from_user.first_name
    c = cfg()
    cdata = c.get("cekilisler", {}).get(chat_id, {})
    if not cdata.get("aktif"):
        return await query.answer("❌ Aktif çekiliş yok!", show_alert=True)
    if uid in cdata.get("katilimcilar", {}):
        return await query.answer("✅ Zaten katıldın!", show_alert=True)
    cdata.setdefault("katilimcilar", {})[uid] = isim
    c["cekilisler"][chat_id] = cdata
    save(c)
    n = len(cdata["katilimcilar"])
    await query.answer(f"✅ Katıldın! Toplam {n} kişi.", show_alert=True)
    try:
        yeni_text = query.message.text + f"\n👥 Katılımcı: {n}"
        await query.edit_message_text(yeni_text, parse_mode="HTML",
            reply_markup=query.message.reply_markup)
    except: pass

# ── /vip ──────────────────────────────────────────────────────
async def vip_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """⭐ /vip — VIP durumu ve bilgileri"""
    c = cfg()
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    bakiye = get_bakiye(c, uid)
    esik = c.get("vip_esik", 10000)
    carpan = c.get("vip_carpan", 1.5)
    vip = is_vip(c, uid)
    if vip:
        await dm_veya_grup(update, context, 
            f"⭐ <b>VIP Üye</b>\n\n"
            f"Tebrikler {isim}! VIP statüsündesin.\n\n"
            f"🎯 Avantajlar:\n"
            f"  • Casino kazançlarında <b>{carpan}x çarpan</b>\n"
            f"  • Özel VIP rozeti 💎\n"
            f"  • Öncelikli destek\n\n"
            f"💰 Mevcut bakiye: <b>{bakiye:,}</b> puan",
            parse_mode="HTML")
    else:
        kalan = max(0, esik - bakiye)
        bar_dolu = min(10, int((bakiye / esik) * 10))
        bar = "█" * bar_dolu + "░" * (10 - bar_dolu)
        await dm_veya_grup(update, context, 
            f"⭐ <b>VIP Sistemi</b>\n\n"
            f"VIP olmak için <b>{esik:,}</b> puana ihtiyacın var.\n\n"
            f"[{bar}] {int((bakiye/esik)*100)}%\n"
            f"💰 Bakiye: {bakiye:,} / {esik:,}\n"
            f"📍 Kalan: <b>{kalan:,}</b> puan\n\n"
            f"🎯 VIP avantajları:\n"
            f"  • {carpan}x casino çarpanı\n"
            f"  • 💎 Elmas rozet\n"
            f"  • Özel komutlara erişim",
            parse_mode="HTML")

# ── /bildirim ─────────────────────────────────────────────────
async def bildirim_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🔔 /bildirim — DM bildirimlerini aç/kapat"""
    c = cfg()
    uid = str(update.effective_user.id)
    kullanicilar = c.get("kullanicilar", {})
    mevcut = kullanicilar.get(uid, {}).get("dm_ok", True)
    yeni = not mevcut
    if uid in kullanicilar:
        kullanicilar[uid]["dm_ok"] = yeni
    else:
        kullanicilar[uid] = {"isim": update.effective_user.first_name, "dm_ok": yeni}
    save(c)
    durum = "🔔 Açık" if yeni else "🔕 Kapalı"
    await update.message.reply_text(
        f"{'🔔' if yeni else '🔕'} DM bildirimleri: <b>{durum}</b>\n\n"
        f"{'Casino sonuçları, bonus ve etkinlik bildirimlerini DM\'den alacaksın.' if yeni else 'Artık DM bildirimi almayacaksın.'}",
        parse_mode="HTML")

# ── /kelime (Kelime Zinciri Oyunu) ───────────────────────────
async def kelime_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🔤 /kelime — Kelime zinciri oyunu başlat"""
    c = cfg()
    if not c.get("bakiye_aktif"): return
    chat_id = str(update.effective_chat.id)
    kelime_oyunlari = c.setdefault("kelime_oyunlari", {})
    if chat_id in kelime_oyunlari:
        oyun = kelime_oyunlari[chat_id]
        son = oyun.get("son_kelime", "?")
        return await update.message.reply_text(
            f"🔤 Kelime zinciri aktif!\n"
            f"Son kelime: <b>{son}</b>\n"
            f"<b>{son[-1].upper()}</b> harfiyle başlayan Türkçe kelime yaz!",
            parse_mode="HTML")
    kelime_oyunlari[chat_id] = {
        "aktif": True, "son_kelime": "kelime",
        "kullanilan": ["kelime"], "skor": {},
        "isimler": {},
    }
    save(c)
    await update.message.reply_text(
        f"🔤 <b>Kelime Zinciri Oyunu Başladı!</b>\n\n"
        f"Kural: Her kelime bir öncekinin <b>son harfiyle</b> başlamalı!\n"
        f"Doğru kelime: <b>+10 puan</b>\n"
        f"Oyunu bitirmek için: /kelime_bitir\n\n"
        f"İlk kelime: <b>KELİME</b>\n"
        f"<b>E</b> harfiyle başlayan kelime yaz! 👇",
        parse_mode="HTML")

async def kelime_mesaj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kelime zinciri oyununda gelen mesajları kontrol et"""
    c = cfg()
    chat_id = str(update.effective_chat.id)
    kelime_oyunlari = c.get("kelime_oyunlari", {})
    if chat_id not in kelime_oyunlari: return False
    oyun = kelime_oyunlari[chat_id]
    if not oyun.get("aktif"): return False
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    metin = (update.message.text or "").strip().lower()
    if len(metin) < 2 or not metin.isalpha(): return False
    son = oyun["son_kelime"]
    beklenen_harf = son[-1]
    if metin[0] != beklenen_harf:
        return False  # sessizce geç
    if metin in oyun["kullanilan"]:
        await update.message.reply_text(f"❌ <b>{metin}</b> daha önce kullanıldı!", parse_mode="HTML")
        return True
    # Geçerli kelime
    odul = 10
    oyun["son_kelime"] = metin
    oyun["kullanilan"].append(metin)
    oyun["skor"][uid] = oyun["skor"].get(uid, 0) + odul
    oyun["isimler"][uid] = isim
    add_puan(c, uid, isim, odul)
    c["kelime_oyunlari"] = kelime_oyunlari
    save(c)
    await update.message.reply_text(
        f"✅ <b>{metin.upper()}</b> +{odul}p\n"
        f"Sıra: <b>{metin[-1].upper()}</b> harfiyle devam!",
        parse_mode="HTML")
    return True

async def kelime_bitir_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin veya herkes: /kelime_bitir"""
    c = cfg()
    chat_id = str(update.effective_chat.id)
    kelime_oyunlari = c.get("kelime_oyunlari", {})
    if chat_id not in kelime_oyunlari:
        return await auto_reply(update, "Aktif kelime oyunu yok.")
    oyun = kelime_oyunlari[chat_id]
    skor = oyun.get("skor", {})
    isimler = oyun.get("isimler", {})
    del kelime_oyunlari[chat_id]
    c["kelime_oyunlari"] = kelime_oyunlari
    save(c)
    if not skor:
        return await auto_reply(update, "🔤 Kelime oyunu bitti! Kimse oynamadı.")
    sirali = sorted(skor.items(), key=lambda x: x[1], reverse=True)
    madalya = ["🥇","🥈","🥉"]
    metin = "🔤 <b>Kelime Zinciri Bitti!</b>\n\n"
    for i, (uid, p) in enumerate(sirali[:5]):
        icon = madalya[i] if i < 3 else f"{i+1}."
        metin += f"{icon} {isimler.get(uid,'?')} — <b>{p} puan</b>\n"
    await update.message.reply_text(metin, parse_mode="HTML")

# ── FLOOD KONTROL ─────────────────────────────────────────────
async def flood_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """True dönerse mesaj flood, işleme devam etme"""
    c = cfg()
    if not c.get("flood_aktif", False): return False
    uid = str(update.effective_user.id)
    if is_admin(int(uid)): return False
    simdi = _time.time()
    flood_limit = c.get("flood_limit", 5)
    flood_sure = c.get("flood_sure", 5)
    kayitlar = c.setdefault("flood_sayac", {})
    gecmis = [t for t in kayitlar.get(uid, []) if simdi - t < flood_sure]
    gecmis.append(simdi)
    kayitlar[uid] = gecmis
    if len(gecmis) > flood_limit:
        try:
            await context.bot.restrict_chat_member(
                update.effective_chat.id, int(uid),
                permissions=ChatPermissions(can_send_messages=False),
                until_date=int(simdi) + 60
            )
            await update.message.reply_text(
                f"⚠️ {update.effective_user.first_name} flood yaptı! 1 dakika susturuldu.")
        except: pass
        return True
    return False

# ── GÜNLÜK İSTATİSTİK JOB ─────────────────────────────────────
async def gunluk_istat_job(context: ContextTypes.DEFAULT_TYPE):
    """Her gece 23:00'de günlük özet gönder"""
    c = cfg()
    stats = c.get("stats", {})
    bakiyeler = c.get("bakiyeler", {})
    casino_bugun = stats.get("casino_oyun", 0)
    toplam_uye = len(bakiyeler)
    jackpot = c.get("jackpot_havuz", 0)
    sirali = sorted([(v.get("bakiye",0), v.get("isim","?"))
                     for v in bakiyeler.values() if isinstance(v,dict)],
                    reverse=True)[:3]
    top_str = "\n".join([f"  {['🥇','🥈','🥉'][i]} {isim}: {b:,}p"
                         for i,(b,isim) in enumerate(sirali)])
    ozet = (
        f"📊 <b>Günlük Özet</b>\n\n"
        f"👥 Toplam üye: {toplam_uye}\n"
        f"🎰 Bugün casino: {casino_bugun}\n"
        f"💎 Jackpot havuz: {jackpot:,}p\n\n"
        f"🏆 Liderler:\n{top_str}"
    )
    for kanal in c.get("kanallar", []):
        kid = kanal.split("|")[0].strip()
        try:
            await context.bot.send_message(kid, ozet, parse_mode="HTML")
        except: pass

# ── /ping & /uptime ───────────────────────────────────────────
_BOT_BASLANGIC = _time.time()

async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🏓 /ping — Bot gecikme testi"""
    import datetime as _dt
    t1 = _time.time()
    msg = await update.message.reply_text("🏓 Pong!")
    t2 = _time.time()
    ms = int((t2-t1)*1000)
    sure = int(_time.time() - _BOT_BASLANGIC)
    saat = sure // 3600; dakika = (sure % 3600) // 60
    await msg.edit_text(
        f"🏓 <b>Pong!</b>\n\n"
        f"⚡ Gecikme: <b>{ms}ms</b>\n"
        f"⏱ Uptime: <b>{saat}s {dakika}dk</b>",
        parse_mode="HTML")

# ── /kazan (günlük mini görev) ────────────────────────────────
async def kazan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/kazan — Reklam izle / mini görev (günlük 3 hak)"""
    c = cfg()
    if not c.get("bakiye_aktif"): return
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    bugun = datetime.now().strftime("%Y-%m-%d")
    kayit = c.setdefault("kazan_kayit", {}).get(uid, {})
    if kayit.get("tarih") == bugun and kayit.get("sayi", 0) >= 3:
        return await update.message.reply_text(
            f"⏰ Bugünkü 3 hakkını kullandın!\n"
            f"Yarın tekrar gel. 🌙", parse_mode="HTML")
    odul = random.randint(20, 80)
    sayi = kayit.get("sayi", 0) + 1 if kayit.get("tarih") == bugun else 1
    c["kazan_kayit"][uid] = {"tarih": bugun, "sayi": sayi}
    add_puan(c, uid, isim, odul)
    save(c)
    kalan = 3 - sayi
    await dm_veya_grup(update, context, 
        f"🎁 <b>Mini Görev Tamamlandı!</b>\n\n"
        f"➕ <b>+{odul} puan</b> kazandın!\n"
        f"📍 Bugün kalan hak: {kalan}/3",
        parse_mode="HTML")


async def oto_job(context):
    c=cfg()
    if not c.get("oto_aktif") or not c.get("oto_mesajlar") or not c.get("kanallar"): return
    mesaj=random.choice(c["oto_mesajlar"])
    for k in c["kanallar"]:
        try:
            kid = k["id"] if isinstance(k, dict) else k.split("|")[0].strip()
            await _gonder(context.bot, kid, mesaj, c.get("oto_medya_tip","yok"), c.get("oto_medya_id",""))
            c.setdefault("stats",{})["oto"] = c.get("stats",{}).get("oto",0) + 1
        except Exception as e: logger.error(f"Oto: {e}")
    save(c)

async def rss_job(context):
    c=cfg()
    if not c.get("rss_aktif") or not c.get("rss_url") or not c.get("rss_kanal"): return
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



# ════════════════════════════════════════════════════════════
#  YENİ KOMUTLAR
#  1. /puanekle /puansil — @mention ile admin puan yönetimi
#  2. Dart, Savas, Düello — eğlenceli sosyal metinler
#  3. /puan — üyenin DM'e giden bakiye özeti
# ════════════════════════════════════════════════════════════

async def puanekle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/puanekle @kullanici [miktar] [sebep]"""
    if not is_admin(update.effective_user.id): return
    if len(context.args) < 2:
        return await auto_reply(update,
            "➕ <b>Puan Ekle</b>\n"
            "Kullanım: /puanekle @kullanici [miktar] [sebep]\n"
            "Örnek: /puanekle @ahmet 500 etkinlik ödülü")
    c = cfg()
    hedef_raw = context.args[0].replace("@","")
    try: miktar = int(context.args[1])
    except: return await auto_reply(update, "❌ Miktar sayı olmalı!")
    sebep = " ".join(context.args[2:]) if len(context.args) > 2 else "Admin tarafından eklendi"
    # UID bul — mention veya numara
    hedef_uid = None
    hedef_isim = hedef_raw
    bakiyeler = c.get("bakiyeler", {})
    # Sayısal UID mi?
    if hedef_raw.isdigit():
        hedef_uid = hedef_raw
        hedef_isim = bakiyeler.get(hedef_raw, {}).get("isim", hedef_raw) if isinstance(bakiyeler.get(hedef_raw), dict) else hedef_raw
    else:
        # Username ile ara
        for uid2, v in bakiyeler.items():
            if isinstance(v, dict):
                k_isim = v.get("isim","").lower()
                k_user = v.get("username","").lower().replace("@","")
                if k_isim == hedef_raw.lower() or k_user == hedef_raw.lower():
                    hedef_uid = uid2
                    hedef_isim = v.get("isim", hedef_raw)
                    break
    if not hedef_uid:
        return await auto_reply(update, f"❌ @{hedef_raw} bulunamadı!\nKullanıcı bota /start atmış olmalı.")
    yeni = add_puan(c, hedef_uid, hedef_isim, miktar)
    save(c)
    # Gruba duyur
    sonuc_msg = await update.message.reply_text(
        f"➕ <b>Puan Eklendi!</b>\n\n"
        f"👤 {hedef_isim}\n"
        f"💰 +{miktar:,} puan\n"
        f"📝 Sebep: {sebep}\n"
        f"💳 Yeni bakiye: {yeni:,}",
        parse_mode="HTML")
    _asyncio.create_task(_auto_delete(sonuc_msg, 10))
    # Kişiye DM bildir
    try:
        await context.bot.send_message(int(hedef_uid),
            f"🎁 <b>Puan Eklendi!</b>\n\n"
            f"➕ +{miktar:,} puan\n"
            f"📝 {sebep}\n"
            f"💳 Yeni bakiye: {yeni:,}",
            parse_mode="HTML")
    except: pass


async def puansil_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/puansil @kullanici [miktar] [sebep]"""
    if not is_admin(update.effective_user.id): return
    if len(context.args) < 2:
        return await auto_reply(update,
            "➖ <b>Puan Sil</b>\n"
            "Kullanım: /puansil @kullanici [miktar] [sebep]\n"
            "Örnek: /puansil @ahmet 200 kural ihlali")
    c = cfg()
    hedef_raw = context.args[0].replace("@","")
    try: miktar = int(context.args[1])
    except: return await auto_reply(update, "❌ Miktar sayı olmalı!")
    sebep = " ".join(context.args[2:]) if len(context.args) > 2 else "Admin tarafından silindi"
    hedef_uid = None
    hedef_isim = hedef_raw
    bakiyeler = c.get("bakiyeler", {})
    if hedef_raw.isdigit():
        hedef_uid = hedef_raw
        hedef_isim = bakiyeler.get(hedef_raw, {}).get("isim", hedef_raw) if isinstance(bakiyeler.get(hedef_raw), dict) else hedef_raw
    else:
        for uid2, v in bakiyeler.items():
            if isinstance(v, dict):
                if v.get("isim","").lower() == hedef_raw.lower() or \
                   v.get("username","").lower().replace("@","") == hedef_raw.lower():
                    hedef_uid = uid2
                    hedef_isim = v.get("isim", hedef_raw)
                    break
    if not hedef_uid:
        return await auto_reply(update, f"❌ @{hedef_raw} bulunamadı!")
    yeni = add_puan(c, hedef_uid, hedef_isim, -miktar)
    save(c)
    sonuc_msg = await update.message.reply_text(
        f"➖ <b>Puan Silindi!</b>\n\n"
        f"👤 {hedef_isim}\n"
        f"💰 -{miktar:,} puan\n"
        f"📝 Sebep: {sebep}\n"
        f"💳 Yeni bakiye: {yeni:,}",
        parse_mode="HTML")
    _asyncio.create_task(_auto_delete(sonuc_msg, 10))
    try:
        await context.bot.send_message(int(hedef_uid),
            f"⚠️ <b>Puan Silindi</b>\n\n"
            f"➖ -{miktar:,} puan\n"
            f"📝 {sebep}\n"
            f"💳 Yeni bakiye: {yeni:,}",
            parse_mode="HTML")
    except: pass


async def puan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/puan — Kendi bakiyeni DM'de gör"""
    c = cfg()
    uid = str(update.effective_user.id)
    isim = update.effective_user.first_name
    b = get_bakiye(c, uid)
    puan = b["puan"]
    sev = hesapla_seviye(c, puan)
    sonraki = sonraki_seviye(c, puan)
    vip = "⭐ VIP" if is_vip(c, uid) else ""
    kalan = max(0, sonraki - puan)
    bar_dolu = min(10, int(((puan % (sonraki or 1)) / max(sonraki,1)) * 10)) if sonraki else 10
    bar = "█" * bar_dolu + "░" * (10 - bar_dolu)
    metin = (
        f"💰 <b>Bakiye Kartın</b> {vip}\n\n"
        f"💳 Puan: <b>{puan:,}</b>\n"
        f"⭐ Seviye: <b>{sev}</b>\n"
        f"[{bar}]\n"
        f"📍 Sonraki seviyeye: {kalan:,} puan\n\n"
        f"/gorev /market /bonus /kazan"
    )
    await dm_veya_grup(update, context, metin, f"💰 Bakiye DM'ine gönderildi!")





# ════════════════════════════════════════════════════════════
#  SPONSOR SİSTEMİ v2
#  Admin: /sponsor_panel → inline adım adım ekleme
#  Üye: /sponsorlar → "SİTE ADI | BONUS" butonlu liste
# ════════════════════════════════════════════════════════════

def _get_sponsorlar(c):
    if "sponsorlar" not in c:
        c["sponsorlar"] = {}
    return c["sponsorlar"]


def _sponsor_buton_yazi(s):
    """Buton yazısı: PRADABET | 500 TL DENEME BONUSU"""
    isim = s.get("isim","?").upper()
    bonus = s.get("bonus","").upper()
    if bonus:
        return f"{isim} | {bonus}"
    return isim


# ── /sponsorlar — Üye görünümü ────────────────────────────────
async def sponsorlar_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = cfg()
    sponsorlar = _get_sponsorlar(c)
    aciklar = {k: v for k, v in sponsorlar.items() if v.get("acik", True)}

    if not aciklar:
        return await update.message.reply_text(
            "⚠️ Şu an aktif sponsor yok.\nYakında eklenecek!")

    butonlar = []
    for sid, s in aciklar.items():
        butonlar.append([InlineKeyboardButton(
            _sponsor_buton_yazi(s),
            url=s.get("link", "https://t.me/")
        )])

    await update.message.reply_text(
        "🎰 <b>Sponsor Siteler</b>\n\n"
        "Siteye gitmek için butona tıkla 👇",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(butonlar)
    )


# ── /sponsor_panel — Admin yönetim paneli ────────────────────
async def sponsor_panel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    context.user_data.pop("sponsor_adim", None)
    context.user_data.pop("sponsor_ekle", None)
    await _sponsor_panel_goster(update.message, cfg())


async def _sponsor_panel_goster(msg_or_query, c, edit=False):
    sponsorlar = _get_sponsorlar(c)
    butonlar = []

    for sid, s in sponsorlar.items():
        durum = "🟢" if s.get("acik", True) else "🔴"
        isim = s.get("isim", sid)
        bonus_kisa = s.get("bonus","")[:20]
        butonlar.append([
            InlineKeyboardButton(
                f"{durum} {isim} — {bonus_kisa}",
                callback_data=f"spadmin_site_{sid}"
            )
        ])

    butonlar.append([
        InlineKeyboardButton("➕ Yeni Sponsor Ekle", callback_data="spadmin_ekle_1")
    ])

    metin = (
        "<b>⚙️ Sponsor Paneli</b>\n\n"
        + ("Henüz sponsor yok.\n\n" if not sponsorlar else
           f"Toplam: {len(sponsorlar)} sponsor\n\n")
        + "🟢 Açık | 🔴 Kapalı\n"
        "Siteye tıkla → düzenle/sil/toggle"
    )
    kb = InlineKeyboardMarkup(butonlar)

    if edit:
        await msg_or_query.edit_message_text(metin, parse_mode="HTML", reply_markup=kb)
    else:
        await msg_or_query.reply_text(metin, parse_mode="HTML", reply_markup=kb)


async def sponsor_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    c = cfg()
    sponsorlar = _get_sponsorlar(c)
    uid = query.from_user.id

    # ── Site detay/yönetim ──
    if data.startswith("spadmin_site_"):
        if not is_admin(uid): return
        sid = data.replace("spadmin_site_", "")
        if sid not in sponsorlar: return
        s = sponsorlar[sid]
        durum_yazi = "🟢 Açık" if s.get("acik", True) else "🔴 Kapalı"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "🔴 Kapat" if s.get("acik", True) else "🟢 Aç",
                callback_data=f"spadmin_toggle_{sid}"
            )],
            [InlineKeyboardButton("✏️ Düzenle", callback_data=f"spadmin_duzenle_{sid}")],
            [InlineKeyboardButton("🗑 Sil", callback_data=f"spadmin_sil_onay_{sid}")],
            [InlineKeyboardButton("◀️ Geri", callback_data="spadmin_panel")],
        ])
        kod_str = f"\n🎟 Kod: <code>{s['kod']}</code>" if s.get("kod") else ""
        await query.edit_message_text(
            f"<b>{s.get('isim','?')}</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"💰 {s.get('bonus','—')}\n"
            f"🔗 {s.get('link','—')}"
            f"{kod_str}\n"
            f"📡 {durum_yazi}",
            parse_mode="HTML", reply_markup=kb
        )

    # ── Toggle aç/kapat ──
    elif data.startswith("spadmin_toggle_"):
        if not is_admin(uid): return
        sid = data.replace("spadmin_toggle_", "")
        if sid in sponsorlar:
            sponsorlar[sid]["acik"] = not sponsorlar[sid].get("acik", True)
            c["sponsorlar"] = sponsorlar
            save(c)
        await _sponsor_panel_goster(query, c, edit=True)

    # ── Silme onayı ──
    elif data.startswith("spadmin_sil_onay_"):
        if not is_admin(uid): return
        sid = data.replace("spadmin_sil_onay_", "")
        if sid not in sponsorlar: return
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Evet Sil", callback_data=f"spadmin_sil_evet_{sid}"),
             InlineKeyboardButton("❌ Vazgeç", callback_data=f"spadmin_site_{sid}")],
        ])
        await query.edit_message_text(
            f"🗑 <b>{sponsorlar[sid].get('isim','?')}</b> silinsin mi?",
            parse_mode="HTML", reply_markup=kb
        )

    elif data.startswith("spadmin_sil_evet_"):
        if not is_admin(uid): return
        sid = data.replace("spadmin_sil_evet_", "")
        isim = sponsorlar.get(sid, {}).get("isim", sid)
        if sid in sponsorlar:
            del sponsorlar[sid]
            c["sponsorlar"] = sponsorlar
            save(c)
        await query.answer(f"🗑 {isim} silindi", show_alert=True)
        await _sponsor_panel_goster(query, c, edit=True)

    # ── Geri ──
    elif data == "spadmin_panel":
        if not is_admin(uid): return
        await _sponsor_panel_goster(query, c, edit=True)

    # ── YENİ SPONSOR EKLEME — 3 adım ──
    # Adım 1: İsim sor
    elif data == "spadmin_ekle_1":
        if not is_admin(uid): return
        context.user_data["sponsor_ekle"] = {}
        await query.edit_message_text(
            "➕ <b>Yeni Sponsor — Adım 1/3</b>\n\n"
            "Sponsor sitenin <b>adını</b> yaz:\n"
            "<i>Örnek: Pradabet</i>\n\n"
            "/iptal ile vazgeç",
            parse_mode="HTML"
        )
        context.user_data["sponsor_adim"] = "isim"

    # ── Düzenleme ──
    elif data.startswith("spadmin_duzenle_"):
        if not is_admin(uid): return
        sid = data.replace("spadmin_duzenle_", "")
        context.user_data["sponsor_duzenle_id"] = sid
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Adı değiştir",  callback_data=f"spduzenle_isim_{sid}")],
            [InlineKeyboardButton("💰 Bonusu değiştir", callback_data=f"spduzenle_bonus_{sid}")],
            [InlineKeyboardButton("🔗 Linki değiştir", callback_data=f"spduzenle_link_{sid}")],
            [InlineKeyboardButton("🎟 Kodu değiştir",  callback_data=f"spduzenle_kod_{sid}")],
            [InlineKeyboardButton("◀️ Geri",           callback_data=f"spadmin_site_{sid}")],
        ])
        await query.edit_message_text(
            f"✏️ <b>{sponsorlar[sid].get('isim','?')}</b> — Ne değiştirmek istiyorsun?",
            parse_mode="HTML", reply_markup=kb
        )

    elif data.startswith("spduzenle_"):
        if not is_admin(uid): return
        parcalar = data.split("_")
        alan = parcalar[1]
        sid = "_".join(parcalar[2:])
        context.user_data["sponsor_duzenle_id"] = sid
        context.user_data["sponsor_duzenle_alan"] = alan
        alan_adi = {"isim":"Ad","bonus":"Bonus","link":"Link","kod":"Promo Kod"}.get(alan, alan)
        await query.edit_message_text(
            f"✏️ Yeni <b>{alan_adi}</b> değerini yaz:\n\n"
            "/iptal ile vazgeç",
            parse_mode="HTML"
        )
        context.user_data["sponsor_adim"] = "duzenle"

    # ── Bonus bildirimi ──
    elif data.startswith("spadmin_bonus_duyur_"):
        if not is_admin(uid): return
        sid = data.replace("spadmin_bonus_duyur_", "")
        context.user_data["sponsor_bonus_sid"] = sid
        context.user_data["sponsor_adim"] = "bonus_mesaj"
        await query.edit_message_text(
            f"📢 <b>{sponsorlar[sid].get('isim','?')}</b> için bonus mesajını yaz:\n\n"
            "/iptal ile vazgeç",
            parse_mode="HTML"
        )


async def sponsor_mesaj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sponsor ekleme/düzenleme adım handler"""
    adim = context.user_data.get("sponsor_adim")
    if not adim: return False
    if not is_admin(update.effective_user.id): return False

    # Fotoğraf geldiyse
    if update.message.photo and adim == "logo":
        foto = update.message.photo[-1]
        context.user_data.setdefault("sponsor_ekle", {})["logo"] = foto.file_id
        context.user_data["sponsor_adim"] = "bonus"
        await update.message.reply_text(
            "3/3 ✍️ Bonus yazısını gir (yoksa 'yok' yaz):\nÖrn: 500 TL Deneme Bonusu",
            reply_markup=geri_kb("sponsor_panel")
        )
        return True

    metin = update.message.text.strip() if update.message.text else ""
    if not metin: return False
    c = cfg()
    sponsorlar = _get_sponsorlar(c)

    # ── Yeni ekleme adımları ──
    if adim == "isim":
        context.user_data["sponsor_ekle"]["isim"] = metin
        sid = metin.lower().replace(" ", "_")[:20]
        context.user_data["sponsor_ekle"]["id"] = sid
        context.user_data["sponsor_adim"] = "link"
        await update.message.reply_text(
            f"✅ Adı: <b>{metin}</b>\n\n"
            "➕ <b>Adım 2/3</b> — Siteye giriş <b>linkini</b> yaz:\n"
            "<i>Örnek: https://pradabet.com/giris</i>",
            parse_mode="HTML"
        )
        return True

    elif adim == "link":
        if not metin.startswith("http"):
            await update.message.reply_text("❌ Link http:// veya https:// ile başlamalı!")
            return True
        context.user_data["sponsor_ekle"]["link"] = metin
        context.user_data["sponsor_adim"] = "bonus"
        isim = context.user_data["sponsor_ekle"].get("isim","?")
        await update.message.reply_text(
            f"✅ Link: {metin}\n\n"
            "➕ <b>Adım 3/3</b> — <b>Bonus bilgisini</b> yaz:\n"
            "<i>Örnek: 500 TL DENEME BONUSU</i>\n\n"
            "Yoksa <b>yok</b> yaz",
            parse_mode="HTML"
        )
        return True

    elif adim == "bonus":
        bonus = "" if metin.lower() == "yok" else metin
        data = context.user_data["sponsor_ekle"]
        sid = data.get("id", data.get("isim","site").lower().replace(" ","_")[:20])
        sponsorlar[sid] = {
            "isim": data["isim"],
            "link": data["link"],
            "bonus": bonus,
            "kod": "",
            "acik": True,
        }
        c["sponsorlar"] = sponsorlar
        save(c)
        context.user_data["sponsor_adim"] = None
        context.user_data["sponsor_ekle"] = {}

        # Önizleme
        onizleme = _sponsor_buton_yazi(sponsorlar[sid])
        await update.message.reply_text(
            f"✅ <b>Sponsor eklendi!</b>\n\n"
            f"Buton görünümü:\n"
            f"[ {onizleme} ]\n\n"
            f"🔗 {data['link']}\n\n"
            f"/sponsor_panel ile yönet",
            parse_mode="HTML"
        )
        return True

    # ── Düzenleme ──
    elif adim == "duzenle":
        sid = context.user_data.get("sponsor_duzenle_id")
        alan = context.user_data.get("sponsor_duzenle_alan")
        if sid and sid in sponsorlar and alan:
            sponsorlar[sid][alan] = metin
            c["sponsorlar"] = sponsorlar
            save(c)
            context.user_data["sponsor_adim"] = None
            await update.message.reply_text(
                f"✅ <b>{sponsorlar[sid]['isim']}</b> güncellendi!\n"
                f"{alan}: <b>{metin}</b>\n\n"
                f"Buton: [ {_sponsor_buton_yazi(sponsorlar[sid])} ]",
                parse_mode="HTML"
            )
        return True

    # ── Bonus duyuru mesajı ──
    elif adim == "bonus_mesaj":
        sid = context.user_data.get("sponsor_bonus_sid")
        if sid and sid in sponsorlar:
            s = sponsorlar[sid]
            kod_str = f"\n🎟 Kod: <code>{s['kod']}</code>" if s.get("kod") else ""
            bildirim = (
                f"🚨 <b>YENİ BONUS — {s['isim'].upper()}</b>\n\n"
                f"{metin}\n\n"
                f"💰 {s.get('bonus','')}"
                f"{kod_str}\n\n"
                f"🔗 <a href='{s['link']}'>{s['isim']}'e Git →</a>"
            )
            gonderildi = 0
            for kanal in c.get("kanallar", []):
                kid = kanal["id"] if isinstance(kanal, dict) else kanal.split("|")[0].strip()
                try:
                    await context.bot.send_message(
                        kid, bildirim, parse_mode="HTML",
                        disable_web_page_preview=True)
                    gonderildi += 1
                except: pass
            context.user_data["sponsor_adim"] = None
            await update.message.reply_text(
                f"✅ {gonderildi} kanala gönderildi!\n\n{bildirim}",
                parse_mode="HTML", disable_web_page_preview=True
            )
        return True

    return False


async def sponsor_bonus_duyur_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/sponsor_bonus [id] — Kanala bonus bildirimi"""
    if not is_admin(update.effective_user.id): return
    c = cfg()
    sponsorlar = _get_sponsorlar(c)
    if not context.args:
        # Liste göster
        if not sponsorlar:
            return await update.message.reply_text("Henüz sponsor yok.")
        butonlar = [[InlineKeyboardButton(
            s.get("isim","?"), callback_data=f"spadmin_bonus_duyur_{sid}"
        )] for sid, s in sponsorlar.items()]
        await update.message.reply_text(
            "📢 Hangi site için bildirim gönderilsin?",
            reply_markup=InlineKeyboardMarkup(butonlar)
        )
        return
    sid = context.args[0].lower()
    if sid not in sponsorlar:
        return await auto_reply(update, f"❌ '{sid}' bulunamadı!")
    context.user_data["sponsor_bonus_sid"] = sid
    context.user_data["sponsor_adim"] = "bonus_mesaj"
    await update.message.reply_text(
        f"📢 <b>{sponsorlar[sid]['isim']}</b> için bonus mesajını yaz:",
        parse_mode="HTML"
    )



# ════════════════════════════════════════════════════════════
#  /commands — Tam komut listesi (admin için kategorili)
#  /start    — Kategorili sekme sistemi (Diğerleri sekmesi)
#  BotCommand — / yazınca autocomplete listesi
# ════════════════════════════════════════════════════════════

KOMUTLAR_KATEGORILER = {
    "💰 Ekonomi & Oyun": [
        ("/bakiye", "Bakiyeni DM'de gör"),
        ("/puan", "Puan kartın"),
        ("/bonus", "Günlük bonus al"),
        ("/hbonus", "Haftalık bonus al"),
        ("/kazan", "Mini görev (günlük 3 hak)"),
        ("/gorev", "Görevleri gör"),
        ("/market", "Marketten ürün al"),
        ("/transfer @user miktar", "Puan gönder"),
        ("/ref", "Referans kodunu gör"),
        ("/top", "Liderlik tablosu"),
        ("/profil", "Profil kartın"),
        ("/seviye", "Seviye bilgisi"),
        ("/vip", "VIP durumu"),
    ],
    "🎰 Casino Oyunları": [
        ("/zar bahis", "Zar at"),
        ("/tura bahis", "Yazı tura"),
        ("/slot bahis", "Slot makinesi"),
        ("/rulet bahis", "Rulet"),
        ("/mines bahis", "Mayın tarlası"),
        ("/balik bahis", "Balık avı 🎣"),
        ("/kart bahis", "Şans kartı"),
        ("/ya bahis", "Yüksek/Alçak"),
        ("/tombala bahis", "Tombala"),
        ("/savas bahis", "Kart savaşı"),
        ("/bowling bahis", "Bowling 🎳"),
        ("/dart bahis", "Dart 🎯"),
        ("/basketbol bahis", "Basketbol"),
        ("/penalti bahis", "Penalti"),
        ("/hediye bahis", "Hediye kutusu"),
        ("/bj bahis", "Kasayla BlackJack"),
    ],
    "🎮 Sosyal Oyunlar": [
        ("/duello @user bahis", "1v1 düello"),
        ("/jackpot", "Jackpot havuzunu gör"),
        ("/quiz", "Bilgi yarışması"),
        ("/kelime", "Kelime zinciri"),
        ("/kazan", "Günlük mini görev"),
    ],
    "⚽ Futbol & Tahmin": [
        ("/maclar", "Güncel maçları gör"),
        ("/tahmin maç_id sonuç", "Maç tahmini yap"),
        ("/tahminlerim", "Tahminlerin"),
        ("/tahmin_top", "Tahmin liderleri"),
        ("/ftahmin", "Hızlı tahmin"),
        ("/kripto", "Kripto fiyatları"),
        ("/btc", "Bitcoin fiyatı"),
        ("/eth", "Ethereum fiyatı"),
    ],
    "📋 Genel": [
        ("/sponsorlar", "Sponsor siteler"),
        ("/rehber", "Rehber & yardım"),
        ("/bildirim", "DM bildirimlerini aç/kapat"),
        ("/kurallar", "Grup kuralları"),
        ("/ping", "Bot hız testi"),
        ("/istat", "Bot istatistikleri"),
    ],
}

KOMUTLAR_ADMIN = {
    "👑 Puan Yönetimi": [
        ("/puanekle @user miktar sebep", "Üyeye puan ekle"),
        ("/puansil @user miktar sebep", "Üyeden puan sil"),
        ("/ver user_id miktar", "Puan ver (ID ile)"),
        ("/al user_id miktar", "Puan al (ID ile)"),
        ("/sifirla user_id", "Puanı sıfırla"),
    ],
    "🛡 Moderasyon": [
        ("/warn @user sebep", "Uyarı ver"),
        ("/ban @user", "Yasakla"),
        ("/kick @user", "At"),
        ("/mute @user süre", "Sustur"),
        ("/unmute @user", "Sesi aç"),
        ("/temizle N", "Son N mesajı sil"),
        ("/yasakekle kelime", "Yasaklı kelime ekle"),
        ("/yasaksil kelime", "Yasaklı kelime sil"),
    ],
    "📢 Yayın & Duyuru": [
        ("/duyuru mesaj", "Kanallara duyuru"),
        ("/etkinlik", "Etkinlik başlat"),
        ("/anket soru|A|B|C", "Anket oluştur"),
        ("/cekilis ödül N", "Çekiliş başlat"),
        ("/dm mesaj", "Tüm üyelere DM"),
    ],
    "⚙️ Ayarlar": [
        ("/sponsor_panel", "Sponsor yönet"),
        ("/sponsor_bonus id", "Bonus bildirimi"),
        ("/quiz N", "Bilgi yarışması başlat"),
        ("/quiz_bitir", "Yarışmayı bitir"),
        ("/quiz_ekle soru|cevap", "Soru ekle"),
        ("/jackpot_cekilis", "Jackpot çekilişi"),
        ("/mac_ekle", "Maç ekle"),
        ("/mac_baslat id", "Maçı başlat"),
        ("/mac_bitir id sonuç", "Maçı bitir"),
        ("/futbol_api_key KEY", "API key ayarla"),
    ],
    "🔧 Sistem": [
        ("/otosil", "Otomatik silme aç/kapat"),
        ("/emojisil", "Emoji filtre aç/kapat"),
        ("/onayla", "Join request onayla"),
        ("/cevap ticket mesaj", "Ticket cevapla"),
        ("/carpan değer", "Casino çarpan ayarla"),
    ],
}


async def commands_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/commands — Tüm komutları kategorili göster"""
    uid = update.effective_user.id
    is_adm = is_admin(uid)

    if is_adm and context.args and context.args[0] == "admin":
        # Admin komutları
        metin = "👑 <b>ADMİN KOMUTLARI</b>\n\n"
        for kategori, komutlar in KOMUTLAR_ADMIN.items():
            metin += f"{kategori}\n"
            for cmd, aciklama in komutlar:
                metin += f"  <code>{cmd}</code> — {aciklama}\n"
            metin += "\n"
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("👥 Üye Komutları", callback_data="cmds_uye_0")
        ]])
    else:
        # Üye komutları — ilk kategori
        kategori_listesi = list(KOMUTLAR_KATEGORILER.keys())
        ilk = kategori_listesi[0]
        komutlar = KOMUTLAR_KATEGORILER[ilk]
        metin = f"📋 <b>KOMUTLAR</b>\n\n{ilk}\n"
        for cmd, aciklama in komutlar:
            metin += f"  <code>{cmd}</code> — {aciklama}\n"

        butonlar = []
        satir = []
        for i, kat in enumerate(kategori_listesi):
            kisa = kat.split(" ")[0]  # sadece emoji
            satir.append(InlineKeyboardButton(kisa, callback_data=f"cmds_uye_{i}"))
            if len(satir) == 3:
                butonlar.append(satir)
                satir = []
        if satir:
            butonlar.append(satir)
        if is_adm:
            butonlar.append([InlineKeyboardButton("👑 Admin Komutları", callback_data="cmds_admin_0")])
        kb = InlineKeyboardMarkup(butonlar)

    await dm_veya_grup(update, context, metin, parse_mode="HTML", reply_markup=kb)


async def commands_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Komut listesi callback"""
    query = update.callback_query
    await query.answer()
    data = query.data
    uid = query.from_user.id
    is_adm = is_admin(uid)

    if data.startswith("cmds_uye_"):
        idx = int(data.replace("cmds_uye_", ""))
        kategori_listesi = list(KOMUTLAR_KATEGORILER.keys())
        if idx >= len(kategori_listesi): idx = 0
        kat = kategori_listesi[idx]
        komutlar = KOMUTLAR_KATEGORILER[kat]
        metin = f"📋 <b>KOMUTLAR</b>\n\n{kat}\n"
        for cmd, aciklama in komutlar:
            metin += f"  <code>{cmd}</code> — {aciklama}\n"

        butonlar = []
        satir = []
        for i, k in enumerate(kategori_listesi):
            kisa = k.split(" ")[0]
            btn_text = f"[{kisa}]" if i == idx else kisa
            satir.append(InlineKeyboardButton(btn_text, callback_data=f"cmds_uye_{i}"))
            if len(satir) == 3:
                butonlar.append(satir)
                satir = []
        if satir:
            butonlar.append(satir)
        if is_adm:
            butonlar.append([InlineKeyboardButton("👑 Admin Komutları", callback_data="cmds_admin_0")])
        await query.edit_message_text(metin, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(butonlar))

    elif data.startswith("cmds_admin_") and is_adm:
        idx = int(data.replace("cmds_admin_", ""))
        kat_listesi = list(KOMUTLAR_ADMIN.keys())
        if idx >= len(kat_listesi): idx = 0
        kat = kat_listesi[idx]
        komutlar = KOMUTLAR_ADMIN[kat]
        metin = f"👑 <b>ADMİN KOMUTLARI</b>\n\n{kat}\n"
        for cmd, aciklama in komutlar:
            metin += f"  <code>{cmd}</code> — {aciklama}\n"

        butonlar = []
        satir = []
        for i, k in enumerate(kat_listesi):
            kisa = k.split(" ")[0]
            btn_text = f"[{kisa}]" if i == idx else kisa
            satir.append(InlineKeyboardButton(btn_text, callback_data=f"cmds_admin_{i}"))
            if len(satir) == 3:
                butonlar.append(satir)
                satir = []
        if satir:
            butonlar.append(satir)
        butonlar.append([InlineKeyboardButton("👥 Üye Komutları", callback_data="cmds_uye_0")])
        await query.edit_message_text(metin, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(butonlar))



# ════════════════════════════════════════════════════════════
#  /start — Yeniden tasarım: Kategorili sekmeli ana panel
# ════════════════════════════════════════════════════════════

def _start_panel_kb(sekme="genel"):
    """Sekmeye göre inline klavye"""

    SEKMELER = {
        "genel": [
            [InlineKeyboardButton("🎰 Casino", callback_data="start_s_casino"),
             InlineKeyboardButton("💰 Ekonomi", callback_data="start_s_ekonomi")],
            [InlineKeyboardButton("⚽ Futbol", callback_data="start_s_futbol"),
             InlineKeyboardButton("🎮 Oyunlar", callback_data="start_s_oyunlar")],
            [InlineKeyboardButton("🎰 Sponsorlar", callback_data="start_s_sponsor"),
             InlineKeyboardButton("📊 İstatistik", callback_data="start_s_istat")],
            [InlineKeyboardButton("⚙️ Diğerleri", callback_data="start_s_diger")],
        ],
        "casino": [
            [InlineKeyboardButton("🎲 Zar", callback_data="start_cmd_zar"),
             InlineKeyboardButton("🪙 Tura", callback_data="start_cmd_tura"),
             InlineKeyboardButton("🎰 Slot", callback_data="start_cmd_slot")],
            [InlineKeyboardButton("🎯 Rulet", callback_data="start_cmd_rulet"),
             InlineKeyboardButton("💣 Mines", callback_data="start_cmd_mines"),
             InlineKeyboardButton("🃏 Kart", callback_data="start_cmd_kart")],
            [InlineKeyboardButton("🎳 Bowling", callback_data="start_cmd_bowling"),
             InlineKeyboardButton("🎯 Dart", callback_data="start_cmd_dart"),
             InlineKeyboardButton("⚔️ Savaş", callback_data="start_cmd_savas")],
            [InlineKeyboardButton("🎣 Balık", callback_data="start_cmd_balik"),
             InlineKeyboardButton("🃏 BlackJack", callback_data="start_cmd_bj"),
             InlineKeyboardButton("🎁 Hediye", callback_data="start_cmd_hediye")],
            [InlineKeyboardButton("◀️ Geri", callback_data="start_s_genel")],
        ],
        "ekonomi": [
            [InlineKeyboardButton("💳 Bakiye", callback_data="start_cmd_bakiye"),
             InlineKeyboardButton("🎁 Bonus", callback_data="start_cmd_bonus")],
            [InlineKeyboardButton("🎁 H.Bonus", callback_data="start_cmd_hbonus"),
             InlineKeyboardButton("⭐ Seviye", callback_data="start_cmd_seviye")],
            [InlineKeyboardButton("📋 Görev", callback_data="start_cmd_gorev"),
             InlineKeyboardButton("🛒 Market", callback_data="start_cmd_market")],
            [InlineKeyboardButton("🔄 Transfer", callback_data="start_cmd_transfer"),
             InlineKeyboardButton("🏆 Lider", callback_data="start_cmd_top")],
            [InlineKeyboardButton("💎 VIP", callback_data="start_cmd_vip"),
             InlineKeyboardButton("🔗 Referans", callback_data="start_cmd_ref")],
            [InlineKeyboardButton("◀️ Geri", callback_data="start_s_genel")],
        ],
        "futbol": [
            [InlineKeyboardButton("⚽ Maçlar", callback_data="start_cmd_maclar"),
             InlineKeyboardButton("🎯 Tahmin", callback_data="start_cmd_ftahmin")],
            [InlineKeyboardButton("📋 Tahminlerim", callback_data="start_cmd_tahminlerim"),
             InlineKeyboardButton("🏆 Tahmin Top", callback_data="start_cmd_tahmin_top")],
            [InlineKeyboardButton("₿ BTC", callback_data="start_cmd_btc"),
             InlineKeyboardButton("Ξ ETH", callback_data="start_cmd_eth"),
             InlineKeyboardButton("💎 Kripto", callback_data="start_cmd_kripto")],
            [InlineKeyboardButton("◀️ Geri", callback_data="start_s_genel")],
        ],
        "oyunlar": [
            [InlineKeyboardButton("⚔️ Düello", callback_data="start_cmd_duello"),
             InlineKeyboardButton("🎰 Jackpot", callback_data="start_cmd_jackpot")],
            [InlineKeyboardButton("🧠 Quiz", callback_data="start_cmd_quiz"),
             InlineKeyboardButton("🔤 Kelime", callback_data="start_cmd_kelime")],
            [InlineKeyboardButton("🎯 Kazan", callback_data="start_cmd_kazan"),
             InlineKeyboardButton("📖 Rehber", callback_data="start_cmd_rehber")],
            [InlineKeyboardButton("◀️ Geri", callback_data="start_s_genel")],
        ],
        "sponsor": [
            [InlineKeyboardButton("🎰 Sponsorları Gör", callback_data="start_cmd_sponsorlar")],
            [InlineKeyboardButton("◀️ Geri", callback_data="start_s_genel")],
        ],
        "istat": [
            [InlineKeyboardButton("📊 İstatistik", callback_data="start_cmd_istat"),
             InlineKeyboardButton("🏓 Ping", callback_data="start_cmd_ping")],
            [InlineKeyboardButton("👤 Profil", callback_data="start_cmd_profil"),
             InlineKeyboardButton("🔔 Bildirim", callback_data="start_cmd_bildirim")],
            [InlineKeyboardButton("◀️ Geri", callback_data="start_s_genel")],
        ],
        "diger": [
            [InlineKeyboardButton("📜 Kurallar", callback_data="start_cmd_kurallar"),
             InlineKeyboardButton("📖 Rehber", callback_data="start_cmd_rehber")],
            [InlineKeyboardButton("🎫 Destek", callback_data="start_cmd_destek"),
             InlineKeyboardButton("🔔 Bildirim", callback_data="start_cmd_bildirim")],
            [InlineKeyboardButton("📋 Komutlar", callback_data="start_cmd_commands"),
             InlineKeyboardButton("📩 DM Filtrele", callback_data="start_cmd_dm_filtre")],
            [InlineKeyboardButton("◀️ Geri", callback_data="start_s_genel")],
        ],
    }
    return InlineKeyboardMarkup(SEKMELER.get(sekme, SEKMELER["genel"]))


def _start_metin(c, sekme="genel"):
    isim = c.get("marka_isim", "SOGTİLLA")
    kanal_say = len(c.get("kanallar", []))
    uyeler = len(c.get("kullanicilar", {}))
    bakiye_say = len(c.get("bakiyeler", {}))
    oyun_say = c.get("toplam_oyun", 0)

    sekmeler = {
        "genel": (
            f"⚡ <b>{isim}</b>\n\n"
            f"📡 Kanal: {kanal_say}  👥 Üye: {uyeler}\n"
            f"💳 Bakiye kayıtlı: {bakiye_say}  🎰 Oyun: {oyun_say}\n\n"
            "Hangi bölüme gitmek istiyorsun? 👇"
        ),
        "casino":   f"🎰 <b>Casino Oyunları</b>\n\nBahis yap, kazan! Min bahis: {c.get('casino_min_bahis',10)} puan",
        "ekonomi":  f"💰 <b>Ekonomi</b>\n\nBakiye, bonus, görev ve daha fazlası",
        "futbol":   f"⚽ <b>Futbol & Kripto</b>\n\nMaç tahminleri ve kripto fiyatları",
        "oyunlar":  f"🎮 <b>Sosyal Oyunlar</b>\n\nDüello, quiz, jackpot ve kelime zinciri",
        "sponsor":  f"🎰 <b>Sponsor Siteler</b>\n\nGüvenilir partner siteleri",
        "istat":    f"📊 <b>İstatistik & Profil</b>",
        "diger":    f"⚙️ <b>Diğerleri</b>\n\nKurallar, rehber, destek ve daha fazlası",
    }
    return sekmeler.get(sekme, sekmeler["genel"])


async def start_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start panel callback"""
    query = update.callback_query
    await query.answer()
    data = query.data
    c = cfg()

    # Sekme geçişi
    if data.startswith("start_s_"):
        sekme = data.replace("start_s_", "")
        await query.edit_message_text(
            _start_metin(c, sekme),
            parse_mode="HTML",
            reply_markup=_start_panel_kb(sekme)
        )

    # Komut kısayolu — butona basınca komutu çalıştır
    elif data.startswith("start_cmd_"):
        cmd = data.replace("start_cmd_", "")
        CMD_MAP = {
            "bakiye": bakiye_cmd, "bonus": bonus_cmd, "hbonus": hbonus_cmd,
            "seviye": seviye_cmd, "gorev": gorev_cmd, "market": market_cmd,
            "profil": profil_cmd, "top": top_cmd, "vip": vip_cmd,
            "ref": ref_cmd, "istat": istat_cmd, "ping": ping_cmd,
            "sponsorlar": sponsorlar_cmd, "rehber": rehber_cmd,
            "bildirim": bildirim_cmd, "kurallar": kurallar_cmd,
            "maclar": maclar_cmd, "tahminlerim": tahminlerim_cmd,
            "tahmin_top": tahmin_top_cmd, "ftahmin": ftahmin_cmd,
            "btc": btc_cmd, "eth": eth_cmd, "kripto": kripto_cmd,
            "jackpot": jackpot_cmd, "quiz": quiz_cmd,
            "commands": commands_cmd,
        }
        fn = CMD_MAP.get(cmd)
        if fn:
            # update.message yok (callback), fake context ile çağır
            class FakeUpdate:
                effective_user = query.from_user
                effective_chat = query.message.chat
                message = query.message
            try:
                await fn(FakeUpdate(), context)
            except:
                await query.answer(f"/{cmd} komutunu kullan", show_alert=True)
        else:
            await query.answer(f"/{cmd} yazarak kullan", show_alert=True)


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
    app.add_handler(CommandHandler("rehber",    rehber_cmd))
    app.add_handler(CommandHandler("dm",          dm_cmd))
    app.add_handler(CommandHandler("dm_filtre",   dm_filtre_cmd))
    app.add_handler(CommandHandler("dm_listesi",  dm_listesi_cmd))
    app.add_handler(CommandHandler("duyuru",      duyuru_cmd))
    app.add_handler(CommandHandler("etkinlik",    etkinlik_cmd))
    # Futbol Tahmin
    app.add_handler(CommandHandler("maclar",      maclar_cmd))
    app.add_handler(CommandHandler("tahmin",      tahmin_cmd))  # casino sayı tahmin
    app.add_handler(CommandHandler("ftahmin",     futbol_tahmin_cmd))  # futbol maç tahmini
    app.add_handler(CommandHandler("tahminlerim", tahminlerim_cmd))
    app.add_handler(CommandHandler("tahmin_top",  tahmin_top_cmd))
    app.add_handler(CommandHandler("mac_ekle",    mac_ekle_isle))
    app.add_handler(CommandHandler("mac_baslat",  mac_baslat_cmd))
    app.add_handler(CommandHandler("mac_bitir",   mac_bitir_cmd))
    app.add_handler(CommandHandler("mac_iptal",   mac_iptal_cmd))
    app.add_handler(CommandHandler("futbol_api_key", futbol_api_key_cmd))
    app.add_handler(CommandHandler("maclar_cek",     maclar_cek_cmd))
    app.add_handler(CommandHandler("futbol_ligler",  futbol_ligler_cmd))
    # ── Quiz ──
    app.add_handler(CommandHandler("quiz",          quiz_cmd))
    app.add_handler(CommandHandler("quiz_bitir",    quiz_bitir_cmd))
    app.add_handler(CommandHandler("quiz_ekle",     quiz_soru_ekle_cmd))
    # ── Düello ──
    app.add_handler(CommandHandler("duello",        duello_cmd))
    app.add_handler(CommandHandler("duel",          duello_cmd))
    # ── Jackpot ──
    app.add_handler(CommandHandler("jackpot",       jackpot_cmd))
    app.add_handler(CommandHandler("jackpot_cekilis", jackpot_cekilis_cmd))
    # ── Kasayla BJ ──
    app.add_handler(CommandHandler("bj",            kbj_cmd))
    app.add_handler(CommandHandler("blackjack",     kbj_cmd))
    # ── Eksik Özellikler ──
    app.add_handler(CommandHandler("temizle",       temizle_cmd))
    app.add_handler(CommandHandler("istat",         istatistik_cmd))
    app.add_handler(CommandHandler("cekilis",       cekilis_cmd))
    app.add_handler(CommandHandler("vip",           vip_cmd))
    app.add_handler(CommandHandler("bildirim",      bildirim_cmd))
    app.add_handler(CommandHandler("kelime",        kelime_cmd))
    app.add_handler(CommandHandler("kelime_bitir",  kelime_bitir_cmd))
    app.add_handler(CommandHandler("ping",          ping_cmd))
    app.add_handler(CommandHandler("kazan",         kazan_cmd))
    app.add_handler(CommandHandler("puanekle",      puanekle_cmd))
    app.add_handler(CommandHandler("puansil",       puansil_cmd))
    app.add_handler(CommandHandler("puan",          puan_cmd))
    # ── Sponsor ──
    app.add_handler(CommandHandler("commands",         commands_cmd))
    app.add_handler(CommandHandler("sponsorlar",       sponsorlar_cmd))
    app.add_handler(CommandHandler("sponsor_panel",    sponsor_panel_cmd))
    app.add_handler(CommandHandler("sponsor_bonus",    sponsor_bonus_duyur_cmd))
    app.add_handler(CallbackQueryHandler(commands_cb,  pattern="^cmds_"))
    app.add_handler(CallbackQueryHandler(start_cb,     pattern="^start_s_"))
    app.add_handler(CallbackQueryHandler(start_cb,     pattern="^start_cmd_"))
    app.add_handler(CallbackQueryHandler(sponsor_cb,   pattern="^spadmin_"))
    app.add_handler(CallbackQueryHandler(sponsor_cb,   pattern="^spduzenle_"))
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
    app.add_handler(CallbackQueryHandler(cekilis_cb,     pattern="^cekilis_"))
    app.add_handler(CallbackQueryHandler(duello_cb,     pattern="^duello_"))
    app.add_handler(CallbackQueryHandler(jackpot_cb,    pattern="^jackpot_"))
    app.add_handler(CallbackQueryHandler(kbj_cb,        pattern="^kbj_"))
    app.add_handler(CallbackQueryHandler(mac_tahmin_cb, pattern="^mac_"))
    app.add_handler(CallbackQueryHandler(rehber_cb, pattern="^rehber_"))
    app.add_handler(CallbackQueryHandler(cb_v2))
    app.add_handler(ChatJoinRequestHandler(join_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, yeni_uye))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, sponsor_mesaj_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, mesaj_handler_v2))

    # Jobs
    app.job_queue.run_repeating(oto_job, interval=3600, first=60)
    app.job_queue.run_repeating(rss_job, interval=3600, first=120)
    # Günlük İstatistik
    app.job_queue.run_daily(gunluk_istat_job, time=datetime.strptime("23:00","%H:%M").time())
    # Futbol API Jobs
    app.job_queue.run_daily(futbol_gunluk_cek_job, time=datetime.strptime("07:00","%H:%M").time())
    app.job_queue.run_repeating(futbol_canli_job, interval=180, first=60)  # Her 3 dk

    print("🚀 SOGTİLLA v5.3 başlatıldı!")
    # BotCommand autocomplete
    cmds = [
        BotCommand("start",    "🏠 Ana panel"),
        BotCommand("puan",     "💰 Bakiyeni gör"),
        BotCommand("bonus",    "🎁 Günlük bonus"),
        BotCommand("commands", "📋 Tüm komutlar"),
        BotCommand("zar",      "🎲 Zar at"),
        BotCommand("slot",     "🎰 Slot oyna"),
        BotCommand("top",      "🏆 Liderlik"),
        BotCommand("iptal",    "❌ İptal"),
    ]
    try:
        import asyncio as _aio2
        _aio2.get_event_loop().run_until_complete(app.bot.set_my_commands(cmds))
    except: pass
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
