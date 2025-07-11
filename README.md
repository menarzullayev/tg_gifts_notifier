# Tez Upgrade | Telegram Gift Notifier

##  overview

**Tez Upgrade** — bu Telegram platformasidagi "Star" sovg'alarini real vaqt rejimida kuzatib borish, yangilari haqida xabar berish va "upgradable" sovg'alarni maxsus topic'li guruhlarda kuzatish uchun mo'ljallangan ilg'or userbot.

Bizning Asosiy Telegram Kanalimiz — [Crypto Games](https://t.me/crypto_click_games)

Bizning "Upgrade Live" Chatimiz — [TezUpgrade](https://t.me/TezUpgrade)

## ⚙️ Asosiy Imkoniyatlar

**Eslatma:** Loyihani ishga tushirish uchun **Python 3.10** yoki undan yuqori versiya talab etiladi.

-   **Yangi Sovg'alarni Aniqlash:** Yangi sovg'alar paydo bo'lganda belgilangan kanalga stiker va batafsil ma'lumot yuboradi.
-   **"Live Upgrade" Kuzatuvi:** "Upgradable" sovg'alar uchun alohida topic ochib, HTTP so'rovlar yordamida yangi "upgrade"larni topadi va havolalarini joylab boradi.
-   **Binary Search:** Yangi to'plam qo'shilganda, joriy "upgrade" ID sini bir necha soniyada **Binary Search** algoritmi orqali avtomatik topadi va yuz minglab keraksiz so'rovlarning oldini oladi.
-   **Admin Boshqaruvi:** Maxsus admin buyruqlari (`/addnew`) orqali tizimga yangi sovg'alar to'plamini osonlikcha qo'shish imkoniyati.
-   **Xavfsiz Konfiguratsiya:** Barcha maxfiy ma'lumotlar muhit o'zgaruvchilari (Environment Variables) orqali boshqariladi va kodingizda saqlanmaydi.

## 🚀 O'rnatish va Ishga Tushirish

1.  **Loyihani yuklab oling:**
    ```sh
    git clone [https://github.com/menarzullayev/tg_gifts_notifier.git](https://github.com/menarzullayev/tg_gifts_notifier.git)
    ```
2.  **Loyiha papkasiga o'ting:**
    ```sh
    cd tg_gifts_notifier
    ```
3.  **Kerakli kutubxonalarni o'rnating:**
    ```sh
    pip install -r requirements.txt
    ```
4.  **Dasturni ishga tushirishdan oldin sozlang (pastdagi bo'limga qarang).**
5.  **Dasturni ishga tushiring:**
    ```sh
    python detector.py
    ```
    Birinchi marta ishga tushirganda, `Pyrogram` sizdan Telegram akkauntingizga kirish uchun kerakli ma'lumotlarni (telefon raqam, parol, tasdiqlash kodi) so'raydi.

## ⚙️ Konfiguratsiya (Muhim!)

Dastur maxfiy ma'lumotlarni **muhit o'zgaruvchilari (Environment Variables)** orqali o'qiydi. Bu ma'lumotlarni ikki xil usulda kiritish mumkin:

#### 1. Mahalliy Kompyuterda Ishlatish Uchun (`.env` fayli)

1.  Loyiha papkasida `.env` nomli fayl yarating.
2.  Quyidagi shablonni o'sha faylga nusxalab, o'zingizning ma'lumotlaringiz bilan to'ldiring:

    ```env
    API_ID=12345678
    API_HASH=your_api_hash_here
    BOT_TOKENS=token1,token2,token3
    ADMIN_IDS=123456789,987654321
    NOTIFY_CHAT_ID=-100...
    UPGRADE_LIVE_CHAT_ID=-100...
    SESSION_NAME=my_account
    ```

#### 2. Serverda Ishlatish Uchun (Render.com)

1.  Render.com'dagi loyihangiz sozlamalariga kiring.
2.  Chap menyudagi **"Environment"** bo'limiga o'ting.
3.  **"Add Environment Variable"** tugmasini bosib, yuqoridagi har bir o'zgaruvchini alohida-alohida qo'shib chiqing. Masalan:
    -   **Key:** `API_ID`, **Value:** `12345678`
    -   **Key:** `API_HASH`, **Value:** `your_api_hash_here`
    -   ...va hokazo.

| O'zgaruvchi | Turi | Tavsif |
| :--- | :--- | :--- |
| **SESSION_NAME** | String | Userbot sessiyasi saqlanadigan fayl nomi. |
| **API_ID** | Integer | `my.telegram.org` saytidan olinadigan shaxsiy API ID'ingiz. |
| **API_HASH** | String | `my.telegram.org` saytidan olinadigan shaxsiy API Hash'ingiz. |
| **BOT_TOKENS** | String | Bot tokenlari (vergul bilan ajratilgan holda). |
| **NOTIFY_CHAT_ID** | Integer | Yangi sovg'alar haqidagi asosiy xabarlar yuboriladigan kanal ID'si. |
| **UPGRADE_LIVE_CHAT_ID** | Integer | "Upgrade" kuzatuvi uchun topic'lar ochiladigan guruh (forum) ID'si. |
| **ADMIN_IDS** | String | Adminlarning Telegram ID'lari (vergul bilan ajratilgan holda). |

## 👨‍💻 Admin Buyruqlari

Ushbu buyruqlar faqat `ADMIN_IDS` ro'yxatidagi foydalanuvchilar tomonidan userbot akkauntiga tegishli istalgan chatda yuborilishi mumkin.

-   `/addnew <nom> <bitta_boshlangich_ID>`
    Tizimga yangi sovg'alar to'plamini qo'shadi. Dastur shu nom bilan topic ochadi va berilgan ID'dan foydalanib, joriy "upgrade" sonini Binary Search orqali avtomatik topadi.
    *Masalan:* `/addnew SnoopDogg 6014591077976114307`

## 📞 Aloqa

Savollar yoki takliflar uchun [muallif bilan bog'laning](https://t.me/menarzullayev/).

---

Agar **TezUpgrade** siz uchun foydali bo'lsa va loyiha rivojini qo'llab-quvvatlashni istasangiz, xayriya qilishingiz mumkin. Sizning hissangiz loyihani yanada yaxshilashga yordam beradi.

## Xayriya usullari

| To'lov Turi | Rekvizitlar |
| :--- | :--- |
| 💳 **HUMO** | `9860 6004 0823 7573` |
| 💳 **UzCard** | `5614 6819 0148 7375` |
| 💳 **Mastercard** | `5477 3300 2178 3679` |
| 💎 **TON** | `UQD6KUkX6M5eXTx5ysO__hR0svpI8UlU_rC2qcEnkxVwYKb8` |

Qo'llab-quvvatlaganingiz uchun tashakkur!
