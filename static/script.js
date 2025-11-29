let selection = { marka: '', model: '', kasa_tipi: '', motor: '', paket: '' };
let currentProblems = [];

async function handleChange(type) {
    const val = document.getElementById(type + '-select').value;
    selection[type] = val;

    const keys = ['marka', 'model', 'kasa_tipi', 'motor', 'paket'];
    let startReset = false;
    keys.forEach(k => {
        if (startReset) {
            selection[k] = '';
            const el = document.getElementById(k + '-select');
            el.innerHTML = '<option value="">Seçiniz</option>';
            el.disabled = true;
        }
        if (k === type) startReset = true;
    });

    document.getElementById('action-buttons').classList.add('hidden');
    document.getElementById('list-trigger-area').classList.add('hidden');
    
    if (!val) return;

    try {
        const res = await fetch('/get_options', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(selection)
        });
        const data = await res.json();

        const map = { 'marka': 'model', 'model': 'kasa_tipi', 'kasa_tipi': 'motor', 'motor': 'paket' };
        const nextKey = map[type];

        if (nextKey && data[nextKey] && data[nextKey].length > 0) {
            const nextEl = document.getElementById(nextKey + '-select');
            nextEl.innerHTML = '<option value="">Seçiniz</option>';
            data[nextKey].forEach(item => {
                let opt = document.createElement('option');
                opt.value = item;
                opt.innerText = item;
                nextEl.appendChild(opt);
            });
            nextEl.disabled = false;
        } else if (type === 'motor') {
            selection.paket = "Tüm paketler";
            enableActions();
        }

    } catch (e) { console.error(e); }
}

async function enableActions() {
    const paketEl = document.getElementById('paket-select');
    if (!paketEl.disabled && paketEl.value) selection.paket = paketEl.value;

    const res = await fetch('/get_problems', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(selection)
    });
    currentProblems = await res.json();

    document.getElementById('action-buttons').classList.remove('hidden');
}

function openModal() {
    const listDiv = document.getElementById('modal-list');
    const subTitle = document.getElementById('modal-subtitle');
    listDiv.innerHTML = '';
    
    subTitle.innerText = `${selection.marka} ${selection.model} (${selection.motor}) için kayıtlı arızalar:`;

    if (currentProblems.length === 0) {
        listDiv.innerHTML = '<p style="text-align:center">Bu araç için kayıtlı kronik sorun bulunamadı.</p>';
    } else {
        currentProblems.forEach(p => {
            listDiv.innerHTML += `
                <div class="modal-list-item">
                    <h4>${p.sorun}</h4>
                    <p><strong>Çözüm:</strong> ${p.cozum} • <strong>Maliyet:</strong> ${p.maliyet}</p>
                </div>
            `;
        });
    }
    
    document.getElementById('problemsModal').classList.add('active');
}

function closeModal() {
    document.getElementById('problemsModal').classList.remove('active');
}

document.getElementById('problemsModal').addEventListener('click', function(e) {
    if (e.target === this) closeModal();
});

async function askAI() {
    const soruInput = document.getElementById('soru-input');
    const soru = soruInput.value.trim();
    const resBox = document.getElementById('ai-cevap');
    const listTriggerArea = document.getElementById('list-trigger-area');

    if (!soru) {
        resBox.innerHTML = '<div class="warning-msg">Lütfen bir soru yazın.</div>';
        return;
    }

    listTriggerArea.classList.add('hidden');
    resBox.innerHTML = '<div style="color: var(--text-sub); text-align:center;">Analiz ediliyor, lütfen bekleyin...</div>';

    try {
        const res = await fetch('/ai_search', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                soru: soru,
                arac_secimi: selection,
                sorunlar: currentProblems
            })
        });
        const data = await res.json();

        if (data.detay) {
            resBox.innerHTML = `<div style="margin-bottom:10px; color:var(--success); font-weight:bold;">${data.cevap}</div>` + data.detay;
        } else {
            resBox.innerHTML = `<div class="warning-msg">${data.cevap}</div>`;
            
            if (data.show_list) {
                listTriggerArea.classList.remove('hidden');
            }
        }

    } catch (e) {
        resBox.innerHTML = '<div class="warning-msg">Sunucu hatası oluştu.</div>';
    }
}