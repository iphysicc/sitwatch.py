# SitWatch API İstemcisi

SitWatch platformu için resmi Python API istemcisi. Bu modül ile SitWatch API'sine kolayca erişebilir ve tüm özellikleri kullanabilirsiniz.

![SitWatch Logo](https://sitwatch.net/logo.png)

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Kurulum](#-kurulum)
- [Hızlı Başlangıç](#-hızlı-başlangıç)
- [Detaylı Kullanım](#-detaylı-kullanım)
  - [Kimlik Doğrulama](#-kimlik-doğrulama)
  - [Video İşlemleri](#-video-işlemleri)
  - [Kullanıcı İşlemleri](#-kullanıcı-işlemleri)
  - [Topluluk İşlemleri](#-topluluk-işlemleri)
- [Örnekler](#-örnekler)
- [Hata Yönetimi](#-hata-yönetimi)
- [Lisans](#-lisans)

## ✨ Özellikler

- ✅ Tam API Desteği
- 🔒 Güvenli Kimlik Doğrulama
- 🎥 Video İşlemleri
- 👥 Kullanıcı İşlemleri
- 💬 Topluluk Özellikleri
- 🔍 Gelişmiş Arama
- 📊 İstatistikler
- 🚀 Async/Await Desteği
- 📝 Kapsamlı Dokümantasyon

## 📦 Kurulum

```bash
pip install sitwatch
```

## 🚀 Hızlı Başlangıç

```python
import asyncio
from sitwatch import SitWatch

async def main():
    # İstemciyi oluştur
    client = SitWatch()
    
    # Giriş yap
    await client.login('kullanici_adi', 'sifre')
    
    # Trend videoları al
    trending = await client.get_trending_videos()
    
    # Sonuçları göster
    for video in trending:
        print(f"{video['title']} - {video['views']} izlenme")

# Çalıştır
asyncio.run(main())
```

## 📚 Detaylı Kullanım

### 🔐 Kimlik Doğrulama

```python
# İstemciyi özel yapılandırma ile oluştur
client = SitWatch({
    'base_url': 'https://api.sitwatch.net/api',
    'token': 'mevcut_token',  # İsteğe bağlı
    'on_token_change': lambda token: print(f'Token değişti: {token}')  # İsteğe bağlı
})

# Giriş yap
response = await client.login('kullanici_adi', 'sifre')

# Token kontrolü
if client.has_valid_token():
    print('Giriş başarılı!')

# Çıkış yap
await client.logout()
```

### 🎥 Video İşlemleri

```python
# Video bilgisi al
video = await client.get_video_info(123)

# Video ara
results = await client.search_videos({
    'query': 'python',
    'sort_by': 'views',
    'page': 1,
    'per_page': 10,
    'filter_approved': True
})

# Trend videoları al
trending = await client.get_trending_videos()

# En son videoları al
latest = await client.get_latest_videos()

# Top 50 videoları al
top50 = await client.get_top50_videos()

# Video raporla
await client.report_video(123, 'Uygunsuz içerik')
```

### 👥 Kullanıcı İşlemleri

```python
# Kullanıcı profili al
profile = await client.get_user_profile('kullanici_adi')

# Kullanıcı videolarını al
videos = await client.get_user_videos(user_id)

# En çok abonesi olanları al
top_users = await client.get_top_subscribers()

# Önerilen kullanıcıları al
recommended = await client.get_recommended_users()

# Aktif kullanıcıları al
active = await client.get_active_users()
```

### 💬 Topluluk İşlemleri

```python
# Topluluk gönderilerini al
posts = await client.get_community_posts({
    'page': 1,
    'per_page': 10
})

# Video yorumlarını al
comments = await client.get_video_comments(video_id)

# İzleme geçmişini al
history = await client.get_watch_history()

# Bildirimleri al
notifications = await client.get_notifications()
```

## 🎯 Örnekler

### Video Arama ve Filtreleme

```python
# Gelişmiş arama örneği
results = await client.search_videos({
    'query': 'python dersleri',
    'type': 'video',
    'sort_by': 'views',
    'page': 1,
    'per_page': 20,
    'filter_approved': True,
    'min_views': 1000,
    'max_duration': 3600,  # 1 saat
    'upload_date_after': '2024-01-01'
})

# Sonuçları işle
for video in results['results']:
    print(f"""
    Başlık: {video['title']}
    İzlenme: {video['views']}
    Süre: {video['duration']} saniye
    Yükleyen: {video['uploader']['username']}
    """)
```

### Token Yönetimi

```python
def on_token_change(token):
    if token:
        # Token'ı kaydet
        save_token(token)
    else:
        # Token'ı sil
        delete_token()

client = SitWatch({
    'on_token_change': on_token_change,
    'token': load_saved_token()  # Kaydedilmiş token'ı yükle
})
```

## ❌ Hata Yönetimi

```python
try:
    await client.login('kullanici_adi', 'yanlis_sifre')
except Exception as e:
    print(f"Hata: {e['message']}")
    print(f"Durum Kodu: {e['status']}")
    if 'data' in e:
        print(f"Detay: {e['data']}")
```

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🤝 İletişim

- Geliştirici: Physic
- GitHub: [github.com/iphysicc](https://github.com/iphysicc)

## 🙏 Teşekkürler

Bu projeyi desteklediğiniz için teşekkürler!