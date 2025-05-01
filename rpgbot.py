import telebot
import random
import json
import os

TOKEN = '7753526794:AAHMllMFw3pKSexatUwM9skNJ6ZCAAdZCy8'
bot = telebot.TeleBot(TOKEN)

DATA_FILE = 'rp_data.json'

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

def veri_yukle():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def veri_kaydet(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def kullanici_kontrol(data, user_id):
    if str(user_id) not in data:
        data[str(user_id)] = {"xp": 0, "altin": 100, "seviye": 1, "can": 100, "envanter": []}

@bot.message_handler(commands=['start'])
def baslat(message):
    data = veri_yukle()
    kullanici_kontrol(data, message.from_user.id)
    veri_kaydet(data)
    bot.send_message(message.chat.id, "🧝‍♂️ RPG dünyasına hoş geldin! Komutlar:\n"
                                      "/profil - Profilini gör\n"
                                      "/gorev - Görev yap, XP ve altın kazan\n"
                                      "/saldir - Başkasına saldır\n"
                                      "/market - Marketi gör\n"
                                      "/satinal <eşya> - Eşya satın al")

@bot.message_handler(commands=['profil'])
def profil_goster(message):
    data = veri_yukle()
    user = data[str(message.from_user.id)]
    envanter = ', '.join(user['envanter']) if user['envanter'] else 'Boş'
    cevap = (f"📜 Profil:\nSeviye: {user['seviye']}\nXP: {user['xp']}\n"
             f"Altın: {user['altin']}\nCan: {user['can']}\nEnvanter: {envanter}")
    bot.send_message(message.chat.id, cevap)

@bot.message_handler(commands=['gorev'])
def gorev_yap(message):
    data = veri_yukle()
    user_id = str(message.from_user.id)
    kullanici_kontrol(data, user_id)
    xp_kazan = random.randint(10, 30)
    altin_kazan = random.randint(5, 20)
    data[user_id]['xp'] += xp_kazan
    data[user_id]['altin'] += altin_kazan

    # Seviye atlama kontrolü
    if data[user_id]['xp'] >= data[user_id]['seviye'] * 100:
        data[user_id]['seviye'] += 1
        data[user_id]['can'] = 100
        bot.send_message(message.chat.id, f"🎉 Seviye atladın! Yeni seviye: {data[user_id]['seviye']}")

    veri_kaydet(data)
    bot.send_message(message.chat.id, f"✅ Görev tamamlandı! +{xp_kazan} XP, +{altin_kazan} altın!")

@bot.message_handler(commands=['saldir'])
def saldir(message):
    data = veri_yukle()
    komut = message.text.split()
    if len(komut) != 2 or not komut[1].isdigit():
        bot.send_message(message.chat.id, "Kullanım: /saldir <kullanici_id>")
        return

    hedef_id = komut[1]
    saldiran_id = str(message.from_user.id)

    if hedef_id == saldiran_id:
        bot.send_message(message.chat.id, "😅 Kendine saldıramazsın.")
        return

    if hedef_id not in data:
        bot.send_message(message.chat.id, "🚫 Bu kullanıcı kayıtlı değil.")
        return

    hasar = random.randint(10, 40)
    data[hedef_id]['can'] -= hasar
    if data[hedef_id]['can'] <= 0:
        data[saldiran_id]['altin'] += 50
        data[hedef_id]['can'] = 100
        bot.send_message(message.chat.id, f"⚔️ {hasar} hasar verdin ve rakibi bayılttın! +50 altın!")
        bot.send_message(hedef_id, "☠️ Bir saldırı sonucu bayıldın! Canın sıfırlandı.")
    else:
        bot.send_message(message.chat.id, f"⚔️ {hasar} hasar verdin! Hedefin kalan canı: {data[hedef_id]['can']}")

    veri_kaydet(data)

@bot.message_handler(commands=['market'])
def market_goster(message):
    bot.send_message(message.chat.id, "🛒 Market:\n"
                                      "✨ iksir - 30 altın (canı yeniler)\n"
                                      "🗡️ kılıç - 100 altın (görsel amaçlı)\n"
                                      "💎 zırh - 150 altın")

@bot.message_handler(commands=['satinal'])
def esya_al(message):
    data = veri_yukle()
    user_id = str(message.from_user.id)
    kullanici_kontrol(data, user_id)
    komut = message.text.split()
    if len(komut) != 2:
        bot.send_message(message.chat.id, "Kullanım: /satinal <eşya>")
        return
    esya = komut[1].lower()

    market = {
        "iksir": {"fiyat": 30, "etki": lambda u: u.update({"can": 100})},
        "kılıç": {"fiyat": 100},
        "zırh": {"fiyat": 150},
    }

    if esya not in market:
        bot.send_message(message.chat.id, "🚫 Böyle bir eşya yok.")
        return

    fiyat = market[esya]["fiyat"]
    if data[user_id]['altin'] < fiyat:
        bot.send_message(message.chat.id, "💰 Yeterli altının yok.")
        return

    data[user_id]['altin'] -= fiyat
    data[user_id]['envanter'].append(esya)

    if "etki" in market[esya]:
        market[esya]["etki"](data[user_id])

    veri_kaydet(data)
    bot.send_message(message.chat.id, f"✅ {esya} satın alındı!")

bot.polling()
