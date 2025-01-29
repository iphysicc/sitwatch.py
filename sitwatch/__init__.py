import requests
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
from datetime import datetime

class SitWatch:
    """
    SitWatch API istemcisi
    Bu sınıf, SitWatch API'si ile etkileşim kurmak için gerekli tüm metodları içerir.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        SitWatch API istemcisini başlatır
        
        Parametreler:
            config (dict): Yapılandırma seçenekleri
                - base_url (str): API'nin temel URL'i (varsayılan: 'https://api.sitwatch.net/api')
                - token (str): Önceden kaydedilmiş token
                - on_token_change (callable): Token değiştiğinde çağrılacak fonksiyon
        """
        if config is None:
            config = {}
            
        self.base_url = config.get('base_url', 'https://api.sitwatch.net/api')
        self.on_token_change = config.get('on_token_change')
        
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
        self.session.timeout = 10
        
        # Başlangıç token'ı varsa ayarla
        self.token = None
        if 'token' in config:
            self.set_token(config['token'])
            
    def set_token(self, token: str) -> None:
        """
        API istekleri için kullanılacak token'ı ayarlar
        
        Parametreler:
            token (str): JWT token
        """
        self.token = token
        self.session.headers['Authorization'] = f'Bearer {token}'
        
        # Token değişikliğini bildir
        if self.on_token_change:
            self.on_token_change(token)
            
    def get_token(self) -> Optional[str]:
        """
        Mevcut token'ı döndürür
        
        Dönüş:
            str|None: Mevcut token veya None
        """
        return self.token
        
    def has_valid_token(self) -> bool:
        """
        Token'ın geçerli olup olmadığını kontrol eder
        
        Dönüş:
            bool: Token'ın geçerli olup olmadığı
        """
        return bool(self.token)
        
    def clear_token(self) -> None:
        """Token'ı temizler"""
        self.token = None
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
            
        # Token değişikliğini bildir
        if self.on_token_change:
            self.on_token_change(None)
            
    def _handle_error(self, error: requests.RequestException) -> Dict[str, Any]:
        """
        Hata durumlarını standart bir formata dönüştürür
        
        Parametreler:
            error: İstek hatası
            
        Dönüş:
            dict: Standartlaştırılmış hata nesnesi
        """
        if hasattr(error, 'response') and error.response is not None:
            return {
                'status': error.response.status_code,
                'data': error.response.json() if error.response.content else None,
                'message': error.response.json().get('message', 'Bir hata oluştu') if error.response.content else 'Bir hata oluştu'
            }
        return {
            'status': 500,
            'message': str(error) or 'Ağ hatası oluştu'
        }
            
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Kullanıcı girişi yapar
        
        Parametreler:
            username (str): Kullanıcı adı
            password (str): Şifre
            
        Dönüş:
            dict: Giriş yanıtı
            
        Hatalar:
            dict: Detaylı hata bilgisi
            
        Örnek:
            client = SitWatch()
            response = await client.login('kullanici_adi', 'sifre')
        """
        try:
            response = self.session.post(f'{self.base_url}/auth/login', json={
                'username': username,
                'password': password
            })
            response.raise_for_status()
            data = response.json()
            
            if data.get('success') and data.get('tokens', {}).get('access_token'):
                self.set_token(data['tokens']['access_token'])
                
            return data
        except requests.RequestException as e:
            if hasattr(e, 'response'):
                raise {
                    'status': e.response.status_code,
                    'message': e.response.json().get('message', 'Sunucu hatası') if e.response.content else 'Sunucu hatası',
                    'data': e.response.json() if e.response.content else None
                }
            elif hasattr(e, 'request'):
                raise {
                    'status': 0,
                    'message': 'Sunucuya erişilemiyor. Lütfen internet bağlantınızı kontrol edin veya daha sonra tekrar deneyin.',
                    'error': str(e)
                }
            else:
                raise {
                    'status': 0,
                    'message': 'İstek oluşturulamadı',
                    'error': str(e)
                }
                
    async def logout(self) -> Dict[str, Any]:
        """
        Kullanıcı oturumunu sonlandırır
        
        Dönüş:
            dict: Çıkış yanıtı
            
        Hatalar:
            dict: Detaylı hata bilgisi
            
        Örnek:
            response = await client.logout()
        """
        try:
            response = self.session.post(f'{self.base_url}/auth/logout')
            response.raise_for_status()
            self.clear_token()
            return response.json()
        except requests.RequestException as e:
            raise self._handle_error(e)
            
    async def register(self, username: str, password: str, email: str, country: str) -> Dict[str, Any]:
        """
        Yeni kullanıcı kaydı oluşturur
        
        Parametreler:
            username (str): Kullanıcı adı
            password (str): Şifre
            email (str): E-posta adresi
            country (str): Ülke
            
        Dönüş:
            dict: Kayıt yanıtı
            
        Hatalar:
            dict: Detaylı hata bilgisi
            
        Örnek:
            response = await client.register('kullanici_adi', 'sifre', 'eposta@ornek.com', 'Türkiye')
        """
        try:
            response = self.session.post(f'{self.base_url}/auth/register', json={
                'username': username,
                'password': password,
                'email': email,
                'country': country
            })
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise self._handle_error(e)
            
    async def get_video_info(self, video_id: int) -> Dict[str, Any]:
        """
        Belirli bir video hakkında detaylı bilgi alır
        
        Parametreler:
            video_id (int): Video ID
            
        Dönüş:
            dict: Video bilgisi
            
        Hatalar:
            dict: Detaylı hata bilgisi
            
        Örnek yanıt:
        {
            'success': True,
            'video': {
                'id': int,
                'title': str,
                'description': str,
                'thumbnail_url': str,
                'video_url': str,
                'upload_date': str,
                'views': int,
                'likes': int,
                'is_approved': bool,
                'uploader': {
                    'id': int,
                    'username': str,
                    'profile_image': str,
                    'subscriber_count': int,
                    'subscribed': bool
                }
            },
            'actions': {
                'liked': bool,
                'disliked': bool
            }
        }
        """
        try:
            response = self.session.get(f'{self.base_url}/videos/{video_id}/info')
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise self._handle_error(e)
            
    async def get_latest_videos(self) -> List[Dict[str, Any]]:
        """
        En son yüklenen videoları alır
        
        Dönüş:
            list: Video listesi
            
        Hatalar:
            dict: Detaylı hata bilgisi
            
        Örnek:
            videos = await client.get_latest_videos()
        """
        try:
            response = self.session.get(f'{self.base_url}/videos/latest')
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise self._handle_error(e)
            
    async def get_trending_videos(self) -> List[Dict[str, Any]]:
        """
        Trend olan videoları alır
        
        Dönüş:
            list: Video listesi
            
        Hatalar:
            dict: Detaylı hata bilgisi
            
        Örnek:
            videos = await client.get_trending_videos()
        """
        try:
            response = self.session.get(f'{self.base_url}/videos/trending')
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise self._handle_error(e)
            
    async def get_top50_videos(self) -> List[Dict[str, Any]]:
        """
        En popüler 50 videoyu alır
        
        Dönüş:
            list: Video listesi
            
        Hatalar:
            dict: Detaylı hata bilgisi
            
        Örnek:
            videos = await client.get_top50_videos()
        """
        try:
            response = self.session.get(f'{self.base_url}/videos/trending/top50')
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise self._handle_error(e)
            
    async def report_video(self, video_id: int, reason: str) -> Dict[str, Any]:
        """
        Bir videoyu raporlar
        
        Parametreler:
            video_id (int): Video ID
            reason (str): Raporlama nedeni
            
        Dönüş:
            dict: Raporlama sonucu
            
        Hatalar:
            dict: Detaylı hata bilgisi
            
        Örnek:
            response = await client.report_video(123, 'Uygunsuz içerik')
        """
        try:
            files = {'reason': (None, reason)}
            response = self.session.post(f'{self.base_url}/videos/{video_id}/report', files=files)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise self._handle_error(e)
            
    async def search_videos(self, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Video araması yapar
        
        Parametreler:
            options (dict): Arama seçenekleri
                - query (str): Arama sorgusu
                - type (str): Arama tipi ('video' | 'channel' | 'trending')
                - sort_by (str): Sıralama ('relevance' | 'views' | 'date' | 'likes' | 'trending')
                - page (int): Sayfa numarası
                - per_page (int): Sayfa başına sonuç
                - filter_approved (bool): Sadece onaylı videolar
                - min_views (int): Minimum görüntülenme
                - max_duration (int): Maksimum süre
                - upload_date_after (str): Bu tarihten sonra
                - upload_date_before (str): Bu tarihten önce
                
        Dönüş:
            dict: Arama sonuçları
            
        Hatalar:
            dict: Detaylı hata bilgisi
            
        Örnek:
            results = await client.search_videos({
                'query': 'python',
                'sort_by': 'views',
                'page': 1,
                'per_page': 10
            })
            
        Örnek yanıt:
        {
            'success': bool,
            'results': [
                {
                    'id': int,
                    'title': str,
                    'description': str,
                    'thumbnail_url': str,
                    'upload_date': str,
                    'views': int,
                    'duration': int,
                    'uploader': {
                        'id': int,
                        'username': str,
                        'profile_image': str
                    },
                    'stats': {
                        'likes': int,
                        'midlikes': int,
                        'dislikes': int,
                        'comments': int
                    }
                }
            ],
            'total': int,
            'page': int,
            'per_page': int,
            'total_pages': int
        }
        """
        if options is None:
            options = {}
            
        try:
            params = {
                'query': options.get('query'),
                'type': options.get('type'),
                'sort_by': options.get('sort_by'),
                'page': options.get('page'),
                'per_page': options.get('per_page'),
                'filter_approved': options.get('filter_approved'),
                'min_views': options.get('min_views'),
                'max_duration': options.get('max_duration'),
                'upload_date_after': options.get('upload_date_after'),
                'upload_date_before': options.get('upload_date_before')
            }
            
            # None değerlerini temizle
            params = {k: v for k, v in params.items() if v is not None}
            
            response = self.session.get(f'{self.base_url}/videos/search', params=params)
            response.raise_for_status()
            return response.json()
                
        except requests.RequestException as e:
            raise self._handle_error(e)
            
    async def get_user_profile(self, username: str) -> Dict[str, Any]:
        """
        Kullanıcı profil bilgilerini alır
        
        Parametreler:
            username (str): Kullanıcı adı
            
        Dönüş:
            dict: Kullanıcı profil bilgileri
            
        Hatalar:
            dict: Detaylı hata bilgisi
            
        Örnek yanıt:
        {
            'id': int,
            'username': str,
            'profile_image': str,
            'banner': str,
            'background_image': str,
            'description': str,
            'country': str,
            'role': str,
            'is_admin': bool,
            'is_founder': bool,
            'is_co_founder': bool,
            'subscriber_count': int,
            'ban_reason': str,
            'last_active': str,
            'song': {
                'id': int,
                'title': str,
                'url': str,
                'start_time': int,
                'is_muted': bool
            },
            'statistic': {
                'video_count': int,
                'view_count': int
            },
            'quote': str | {
                'quote': str,
                'author': str
            }
        }
        """
        try:
            response = self.session.get(f'{self.base_url}/users/username/{username}')
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise self._handle_error(e)
            
    async def get_user_videos(self, user_id: int) -> Dict[str, Any]:
        """
        Kullanıcının videolarını alır
        
        Parametreler:
            user_id (int): Kullanıcı ID
            
        Dönüş:
            dict: Kullanıcının videoları
            
        Hatalar:
            dict: Detaylı hata bilgisi
            
        Örnek:
            videos = await client.get_user_videos(123)
        """
        try:
            response = self.session.get(f'{self.base_url}/users/{user_id}/videos')
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise self._handle_error(e)
            
    async def get_top_subscribers(self) -> Dict[str, Any]:
        """
        En çok abonesi olan kullanıcıları listeler
        
        Dönüş:
            dict: En çok abonesi olan kullanıcılar listesi
            
        Hatalar:
            dict: Detaylı hata bilgisi
            
        Örnek:
            users = await client.get_top_subscribers()
        """
        try:
            response = self.session.get(f'{self.base_url}/users/top/subscribers')
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise self._handle_error(e)
            
    async def get_recommended_users(self) -> Dict[str, Any]:
        """
        Önerilen kullanıcıları alır
        
        Dönüş:
            dict: Önerilen kullanıcılar listesi
            
        Hatalar:
            dict: Detaylı hata bilgisi
            
        Örnek:
            users = await client.get_recommended_users()
        """
        try:
            response = self.session.get(f'{self.base_url}/users/recommend')
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise self._handle_error(e)
            
    async def get_active_users(self) -> Dict[str, Any]:
        """
        Aktif kullanıcıları alır
        
        Dönüş:
            dict: Aktif kullanıcılar listesi
            
        Hatalar:
            dict: Detaylı hata bilgisi
            
        Örnek:
            users = await client.get_active_users()
        """
        try:
            response = self.session.get(f'{self.base_url}/users/active')
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise self._handle_error(e)
            
    async def get_user_posts(self, user_id: int, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Kullanıcının topluluk gönderilerini alır
        
        Parametreler:
            user_id (int): Kullanıcı ID
            options (dict): Sayfalama seçenekleri
                - page (int): Sayfa numarası (varsayılan: 1)
                - per_page (int): Sayfa başına gönderi sayısı (varsayılan: 10)
                
        Dönüş:
            dict: Kullanıcının gönderileri
            
        Hatalar:
            dict: Detaylı hata bilgisi
            
        Örnek:
            posts = await client.get_user_posts(123, {'page': 1, 'per_page': 10})
        """
        if options is None:
            options = {}
            
        try:
            params = {
                'page': options.get('page', 1),
                'per_page': options.get('per_page', 10)
            }
            
            response = self.session.get(f'{self.base_url}/users/{user_id}/community/paged', params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise self._handle_error(e)
            
    async def get_my_subscriptions(self) -> List[Dict[str, Any]]:
        """
        Giriş yapmış kullanıcının aboneliklerini alır
        
        Dönüş:
            list: Abonelik listesi
            
        Hatalar:
            dict: Detaylı hata bilgisi
            
        Örnek:
            subscriptions = await client.get_my_subscriptions()
        """
        try:
            response = self.session.get(f'{self.base_url}/me/subscriptions')
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise self._handle_error(e)
            
    async def get_community_posts(self, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Sayfalanmış topluluk gönderilerini alır
        
        Parametreler:
            options (dict): Sayfalama seçenekleri
                - page (int): Sayfa numarası (varsayılan: 1)
                - per_page (int): Sayfa başına gönderi sayısı (varsayılan: 10)
                
        Dönüş:
            dict: Topluluk gönderileri
            
        Hatalar:
            dict: Detaylı hata bilgisi
            
        Örnek yanıt:
        {
            'success': bool,
            'posts': [
                {
                    'id': int,
                    'content': str,
                    'created_at': str,
                    'comments_count': int,
                    'image': str,
                    'uploader': {
                        'username': str,
                        'profile_image': str,
                        'subscriber_count': int
                    },
                    'actions': {
                        'likes': int,
                        'midlikes': int,
                        'dislikes': int
                    }
                }
            ],
            'total': int,
            'pages': int,
            'has_next': bool,
            'has_prev': bool
        }
        """
        if options is None:
            options = {}
            
        try:
            params = {
                'page': options.get('page', 1),
                'per_page': options.get('per_page', 10)
            }
            
            response = self.session.get(f'{self.base_url}/community/posts/paged', params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise self._handle_error(e)
            
    async def get_video_comments(self, video_id: int) -> List[Dict[str, Any]]:
        """
        Video yorumlarını alır
        
        Parametreler:
            video_id (int): Video ID
            
        Dönüş:
            list: Yorum listesi
            
        Hatalar:
            dict: Detaylı hata bilgisi
            
        Örnek yanıt:
        [
            {
                'comment_id': int,
                'content': str,
                'username': str,
                'user_avatar': str,
                'created_at': str,
                'user_id': int,
                'parent_id': int,
                'edited_at': str,
                'is_edited': bool
            }
        ]
        """
        try:
            response = self.session.get(f'{self.base_url}/videos/{video_id}/comments')
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise self._handle_error(e)
            
    async def get_watch_history(self) -> List[Dict[str, Any]]:
        """
        Kullanıcının video izleme geçmişini alır
        
        Dönüş:
            list: İzleme geçmişi
            
        Hatalar:
            dict: Detaylı hata bilgisi
            
        Örnek yanıt:
        [
            {
                'video_id': str,
                'title': str,
                'thumbnail': str,
                'viewed_at': str
            }
        ]
        """
        try:
            response = self.session.get(f'{self.base_url}/library/history')
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise self._handle_error(e)
            
    async def get_studio_videos(self) -> Dict[str, Any]:
        """
        İçerik üreticinin video listesini alır
        
        Dönüş:
            dict: Stüdyo videoları
            
        Hatalar:
            dict: Detaylı hata bilgisi
            
        Örnek yanıt:
        {
            'videos': [
                {
                    'id': int,
                    'title': str,
                    'description': str,
                    'thumbnail_url': str,
                    'upload_date': str,
                    'views': int,
                    'is_approved': bool,
                    'is_visible': bool,
                    'duration': int,
                    'filename': str,
                    'delete_reason': str,
                    'actions': {
                        'likes': int,
                        'dislikes': int,
                        'midlikes': int
                    }
                }
            ]
        }
        """
        try:
            response = self.session.get(f'{self.base_url}/studio/videos')
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise self._handle_error(e)
            
    async def get_notifications(self) -> List[Dict[str, Any]]:
        """
        Kullanıcı bildirimlerini alır
        
        Dönüş:
            list: Bildirim listesi
            
        Hatalar:
            dict: Detaylı hata bilgisi
            
        Örnek yanıt:
        [
            {
                'id': int,
                'message': str,
                'type': str,
                'time_ago': str,
                'sender_image': str,
                'sender_username': str,
                'read': bool
            }
        ]
        """
        try:
            response = self.session.get(f'{self.base_url}/notifications')
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise self._handle_error(e) 