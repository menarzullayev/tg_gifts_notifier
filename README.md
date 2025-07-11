# Tez Upgrade | Gift upgrades

## Overview

**Tez Upgrade** — bu Telegram platformasidagi sovg'alarni real vaqt rejimida kuzatib borish, yangilari haqida xabar berish va "upgradable" sovg'alarni maxsus topic'li guruhlarda kuzatish uchun mo'ljallangan ilg'or userbot.

Bizning Asosiy Telegram Kanalimiz — [Crypto Games](https://t.me/crypto_click_games)

Bizning "Upgrade Live" chatimiz — [TezUpgrade](https://t.me/TezUpgrade)

## ⚙️ Asosiy Imkoniyatlar

**Eslatma:** Loyihani ishga tushirish uchun **Python 3.10** yoki undan yuqori versiya talab etiladi.

  - **Yangi Sovg'alarni Aniqlash:** Yangi sovg'alar paydo bo'lganda belgilangan kanalga stiker va batafsil ma'lumot yuboradi.
  - **"Live Upgrade" Kuzatuvi:** "Upgradable" sovg'alar uchun alohida topic ochib, HTTP so'rovlar yordamida yangi "upgrade"larni topadi va havolalarini joylab boradi.
  - **Binary Search:** Yangi to'plam qo'shilganda, joriy "upgrade" ID sini bir necha soniyada **Binary Search** algoritmi orqali avtomatik topadi va yuz minglab keraksiz so'rovlarning oldini oladi.
  - **Admin Boshqaruvi:** Maxsus admin buyruqlari (`/addnew`) orqali tizimga yangi sovg'alar to'plamini osonlikcha qo'shish imkoniyati.
  - **Moslashuvchan Sozlamalar:** Barcha kerakli parametrlarni `config.py` fayli orqali osonlikcha boshqarish.

## 🚀 O'rnatish va Ishga Tushirish

1.  **Loyihani yuklab oling:**
    ```sh
    git clone https://github.com/menarzullayev/tg_gifts_notifier.git
    ```
2.  **Loyiha papkasiga o'ting:**
    ```sh
    cd tg_gifts_notifier
    ```
3.  **Kerakli kutubxonalarni o'rnating:**
    ```sh
    pip install -r requirements.txt
    ```
4.  **Dasturni ishga tushiring:**
    ```sh
    python detector.py
    ```
    Birinchi marta ishga tushirganda, `Pyrogram` sizdan Telegram akkauntingizga kirish uchun kerakli ma'lumotlarni (telefon raqam, parol, tasdiqlash kodi) so'raydi.

## ⚙️ Konfiguratsiya (`config.py`)

Dasturni ishlatishdan oldin, `config.py` faylini ochib, quyidagi maydonlarni o'zingizning ma'lumotlaringiz bilan to'ldirishingiz shart.

| Maydon | Turi | Tavsif |
| :--- | :--- | :--- |
| **SESSION\_NAME** | String | Userbot sessiyasi saqlanadigan fayl nomi (masalan, `"my_account"`). |
| **API\_ID** | Integer | `my.telegram.org` saytidan olinadigan shaxsiy API ID'ingiz. |
| **API\_HASH** | String | `my.telegram.org` saytidan olinadigan shaxsiy API Hash'ingiz. |
| **BOT\_TOKENS** | List[String] | `@BotFather` orqali olingan bot(lar)ingizning tokenlari ro'yxati. |
| **NOTIFY\_CHAT\_ID** | Integer | Yangi sovg'alar haqidagi asosiy xabarlar yuboriladigan kanal ID'si. |
| **UPGRADE\_LIVE\_CHAT\_ID** | Integer | "Upgrade" kuzatuvi uchun topic'lar ochiladigan guruh (forum) ID'si. |
| **ADMIN\_IDS** | List[Integer] | Dasturni buyruqlar orqali boshqara oladigan adminlarning Telegram ID'lari. |
| **CHECK\_INTERVAL** | Float | Yangi sovg'alarni tekshirish oralig'i (soniya). |
| **UPGRADE\_CHECK\_INTERVAL**| Float | "Upgrade"larni tekshirish oralig'i (soniya). |
| **FOOTER\_TEXT** | String | Har bir xabar oxiriga qo'shiladigan reklama matni. |

## 👨‍💻 Admin Buyruqlari

Ushbu buyruqlar faqat `ADMIN_IDS` ro'yxatidagi foydalanuvchilar tomonidan userbot akkauntiga tegishli istalgan chatda yuborilishi mumkin.

  - `/addnew <nom> <gift_ID>`
    Tizimga yangi sovg'alar to'plamini qo'shadi. Dastur shu nom bilan topic ochadi va berilgan ID'dan foydalanib, joriy "upgrade" sonini Binary Search orqali avtomatik topadi.
    *Masalan:* `/addnew SnoopDogg 6014591077976114307`

## 📞 Aloqa

Savollar yoki takliflar uchun [muallif bilan bog'laning](https://t.me/menarzullayev/).

-----

Agar **TezUpgrade** siz uchun foydali bo'lsa va loyiha rivojini qo'llab-quvvatlashni istasangiz, xayriya qilishingiz mumkin. Sizning hissangiz loyihani yanada yaxshilashga yordam beradi.

## Xayriya usullari
    - **HUMO** `9860 6004 0823 7573`
    - **UzCard**  `5614 6819 0148 7375`
    - **Mastercard**  `5477 3300 2178 3679`
    - **TON**  `UQD6KUkX6M5eXTx5ysO__hR0svpI8UlU_rC2qcEnkxVwYKb8`

Qo'llab-quvvatlaganingiz uchun tashakkur\!