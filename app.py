import json
import re
from flask import Flask, render_template, request, jsonify
from ollama import Client

app = Flask(__name__)
client = Client(host='http://localhost:11434')

def load_data():
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Hata: {e}")
        return []

def load_sabity_cevap_data():
    try:
        with open('general_responses.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Hata: general_responses.json yüklenemedi: {e}")
        return []

SABIT_CEVAP_DATASET = load_sabity_cevap_data()

@app.route('/')
def index():
    data = load_data()
    markalar = sorted(list(set(i['marka'].strip() for i in data if 'marka' in i)))
    return render_template('index.html', markalar=markalar)

@app.route('/get_options', methods=['POST'])
def get_options():
    data = load_data()
    s = request.json
    marka = s.get('marka', '').strip()
    model = s.get('model', '').strip()
    kasa = s.get('kasa_tipi', '').strip()
    motor = s.get('motor', '').strip()
    
    filtrelenmis = data
    
    if marka: filtrelenmis = [i for i in filtrelenmis if i.get('marka', '').strip() == marka]
    if model: filtrelenmis = [i for i in filtrelenmis if i.get('model', '').strip() == model]
    if kasa: filtrelenmis = [i for i in filtrelenmis if i.get('kasa_tipi', '').strip() == kasa]
    if motor: filtrelenmis = [i for i in filtrelenmis if i.get('motor', '').strip() == motor]
    
    opsiyonlar = {}
    
    if marka and not model:
        opsiyonlar['model'] = sorted(list(set(i['model'].strip() for i in filtrelenmis if 'model' in i)))
    elif model and not kasa:
        opsiyonlar['kasa_tipi'] = sorted(list(set(i['kasa_tipi'].strip() for i in filtrelenmis if 'kasa_tipi' in i)))
    elif kasa and not motor:
        opsiyonlar['motor'] = sorted(list(set(i['motor'].strip() for i in filtrelenmis if 'motor' in i)))
    elif motor:
        paketler = set()
        for i in filtrelenmis:
            if i.get('paket'):
                parts = i['paket'].replace(',', '/').split('/')
                for part in parts:
                    paketler.add(part.strip())
        opsiyonlar['paket'] = sorted(list(paketler))
    
    return jsonify(opsiyonlar)

@app.route('/get_problems', methods=['POST'])
def get_problems():
    data = load_data()
    s = request.json
    sonuc = [
        i for i in data
        if i['marka'].strip() == s.get('marka', '').strip()
        and i['model'].strip() == s.get('model', '').strip()
        and i['kasa_tipi'].strip() == s.get('kasa_tipi', '').strip()
        and i['motor'].strip() == s.get('motor', '').strip()
    ]
    return jsonify(sonuc[0]['sorunlar'] if sonuc else [])

def check_sabity_cevap(soru):
    soru_lower = soru.lower()
    for item in SABIT_CEVAP_DATASET:
        text_match = any(match in soru_lower for match in item['TEXT_MATCH'])
        if text_match:
            return item['RESPONSE']
            
    return None
@app.route('/ai_search', methods=['POST'])
def ai_search():
    try:
        req = request.json
        soru = req.get('soru')
        arac = req.get('arac_secimi')
        sorunlar = req.get('sorunlar')
        
        if not sorunlar:
            return jsonify({'cevap': 'Lütfen önce araç seçimini tamamlayın.', 'detay': None, 'show_list': False})
        
        sabity_cevap = check_sabity_cevap(soru)
        if sabity_cevap:
            return jsonify({'cevap': sabity_cevap, 'detay': None, 'show_list': False})
            
        sorun_listesi_str = '\n'.join([f"- {s['sorun']}" for s in sorunlar])
        
        system_prompt = (
            f"Sen uzman bir araç teknisyenisin. Seçilen Araç: {arac['marka']} {arac['model']}.\n"
            f"Veri Tabanındaki Kronik Sorunlar:\n{sorun_listesi_str}\n\n"
            "ÇOK ÖNEMLİ KURALLAR: SADECE AŞAĞIDAKİ 3 KURALDAN BİRİNİN CEVABINI VER. BAŞKA HİÇBİR AÇIKLAMA EKLEME.\n"
            "DURUM 1 (Alakasız): Eğer soru 'Naber', 'Nasılsın' gibi sohbet ise veya seçilen araçla/arıza ile tamamen alakasızsa:\n"
            "Cevap olarak tam olarak şunu yaz: 'Lütfen sadece seçtiğiniz araç hakkında soru sorun.'\n\n"
            "DURUM 2 (Kronik Değil): Eğer soru seçilen araçla ilgili bir arıza belirtisi ise AMA bu sorun listedeki 'Kronik Sorunlar'da YOKSA:\n"
            "Cevap olarak tam olarak şunu yaz: 'Üzgünüm, böyle bir sorun kayıtlarımda bulunmamaktadır. GENEL_LISTE_BUTONU.'\n\n"
            "DURUM 3 (Kronik Sorun): Eğer soru yukarıdaki 'Kronik Sorunlar' listesindeki bir sorunla eşleşiyorsa:\n"
            "Cevap olarak sadece listedeki o sorunun başlığını (textini) yaz. Başka hiçbir şey ekleme."
        )
        response = client.generate(
            model='llama3.1:8b',
            prompt=f"{system_prompt}\n\nKullanıcı Sorusu: {soru}",
            stream=False,
            options={'temperature': 0.0}
        )
        
        ai_cevap = response['response'].strip().replace("'", "").replace('"', "")
        
        ai_cevap = ai_cevap.split('\n')[-1].strip()
        
        if "göre cevap vermem gerekir" in ai_cevap:
            ai_cevap = ai_cevap.split('göre cevap vermem gerekir')[-1].split("Cevap olarak:")[0].strip()
        
        if "nedeniyle" in ai_cevap:
            ai_cevap = ai_cevap.split("nedeniyle")[-1].strip()
            
        ai_cevap = ai_cevap.replace(":", "").strip()
        if ai_cevap.lower().startswith("cevap"):
             ai_cevap = ai_cevap[len("cevap"):].strip()
        
        final_cevap = ai_cevap.strip()
        if final_cevap and not final_cevap.endswith(".") and not final_cevap.endswith("!") and not final_cevap.endswith("?"):
            final_cevap += "."
        
        show_list = False
        
        if "GENEL_LISTE_BUTONU" in final_cevap:
            final_cevap = final_cevap.replace(". GENEL_LISTE_BUTONU", "").replace("GENEL_LISTE_BUTONU", "").strip() + "."
            show_list = True
            return jsonify({'cevap': final_cevap, 'detay': None, 'show_list': show_list})
        
        if "Lütfen sadece" in final_cevap or "Üzgünüm" in final_cevap:
             return jsonify({'cevap': final_cevap, 'detay': None, 'show_list': show_list})

        ilgili_sorun = next((s for s in sorunlar if s['sorun'] in final_cevap or final_cevap.strip(".") in s['sorun']), None)
        
        if ilgili_sorun:
            detay_html = (
                f"<div class='ai-result-card'>"
                f"<h3>⚠️ {ilgili_sorun['sorun']}</h3>"
                f"<div class='detail-grid'>"
                f"<div><strong>Kronik mi?</strong> <span class='badge {str(ilgili_sorun['kronik_mi']).lower()}'>{ 'Evet' if ilgili_sorun['kronik_mi'] else 'Hayır' }</span></div>"
                f"<div><strong>Etkilenme:</strong> {ilgili_sorun['etkilenme_orani']}</div>"
                f"</div>"
                f"<p class='solution'><strong>🛠️ Çözüm:</strong> {ilgili_sorun['cozum']}</p>"
                f"<p class='cost'><strong>💰 Tahmini Maliyet:</strong> {ilgili_sorun['maliyet']}</p>"
                f"</div>"
            )
            return jsonify({'cevap': 'Sorununuz veri tabanımızda bulundu:', 'detay': detay_html, 'show_list': False})
        else:
            return jsonify({'cevap': final_cevap, 'detay': None, 'show_list': False})
            
    except Exception as e:
        return jsonify({'cevap': f'Sistem hatası: {str(e)}', 'detay': None, 'show_list': False})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)