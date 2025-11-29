# Otomobil Kronik Arıza Rehberi AI 

### Yapay Zeka Teknolojisiyle Geliştirilmiş Akıllı Otomobil Arıza Analiz Platformu

Bu proje, **Yapay Zeka teknolojisinin gücüyle** elde edilen kapsamlı veri analizi ile popüler otomobil modellerine ait **kronikleşmiş arızaları** ve bu arızaların **tahmini çözüm maliyetlerini** sunan akıllı bir rehber uygulamasıdır. Kullanıcıların seçtiği model ve motor tipine göre özelleştirilmiş sorun listeleri sunar.

---

##  Temel Özellikler

| Kategori | Özellik | Açıklama |
| :--- | :--- | :--- |
| **Model Tespiti** | Model Bazlı Arıza | Seçilen araç **marka, model, kasa tipi ve motor** özelliklerine özel kronik sorun listesi sunar. |
| **Sorgulama** | Akıllı Analiz | Kullanıcıların doğal dilde sorduğu arıza belirtilerini analiz ederek, sorunun veri tabanımızdaki kronik sorunlarla eşleşip eşleşmediğini belirler. |
| **Acil Durum** | Sabit Çözümler | Lastik patlaması, yakıt bitmesi gibi genel ve acil durumlar için **kesin ve sabit** çözüm talimatları sunar. |
| **Sürüm** | BETA Versiyon | Uygulamanın geliştirme aşamasında olduğunu belirten şeffaf bilgi paylaşımı ve uyarılar içerir. |

---

## Teknoloji Yığını

| Bileşen | Açıklama |
| :--- | :--- |
| **Backend Çerçevesi** | **Python / Flask** (Hızlı ve hafif web sunucusu için) |
| **Veri Analiz Motoru** | **Ollama** ile yerel olarak çalışan gelişmiş dil modeli (Örn: Llama3.1) |
| **Veri Depolama** | **JSON** dosyaları (Kolay taşınabilirlik ve yönetim) |
| **Kullanıcı Arayüzü** | HTML, CSS, JavaScript (Modern ve hızlı arayüz) |

---

## Veri Seti Hakkında (Verinin Gücü)

Bu projenin temelini oluşturan **kronik arıza veri seti (`data.json`)**, geleneksel yöntemlerle toplanmamış, **Yapay Zeka Teknolojisi kullanılarak derinlemesine veri taraması** sonucu oluşturulmuştur. Bu sayede, geniş bir veri yelpazesinden elde edilen bilgi, yapılandırılmış bir rehber haline getirilmiştir.

***

> **ÖNEMLİ UYARI**
>
> Sunulan tüm çözümler ve maliyet tahminleri otomatik veri analizi çıktılarıdır ve yalnızca **bilgilendirme amaçlıdır**. Herhangi bir tamir veya müdahale işlemine başlamadan önce mutlaka **yetkili bir servise** danışılmalıdır. Proje, profesyonel otomotiv danışmanlığı yerine geçmez.

***

## Kurulum ve Çalıştırma

Projeyi yerel makinenizde hızla ayağa kaldırmak için aşağıdaki adımları izleyin:

### 1. Depoyu Klonlayın

```bash
git clone [https://github.com/ismailoksuz/Otomobil-Kronik-Ariza-Rehberi-AI.git](https://github.com/ismailoksuz/Otomobil-Kronik-Ariza-Rehberi-AI.git)
cd Otomobil-Kronik-Ariza-Rehberi-AI
