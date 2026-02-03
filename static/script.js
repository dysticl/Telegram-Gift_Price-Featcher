// Initialize Telegram WebApp
const tg = window.Telegram.WebApp;
tg.expand(); // Make it full screen

// Theme handling
document.body.style.backgroundColor = tg.themeParams.bg_color || '#1a1a1a';
document.body.style.color = tg.themeParams.text_color || '#ffffff';

async function fetchPortfolio() {
    const grid = document.getElementById('gift-grid');
    const totalValEl = document.getElementById('total-value');
    const totalItemsEl = document.getElementById('total-items');

    try {
        const response = await fetch('/api/portfolio');
        const data = await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        // Update Header
        totalValEl.innerText = data.total_value_ton.toFixed(2);
        totalItemsEl.innerText = `${data.total_items} Gifts found`;

        // Clear Grid
        grid.innerHTML = '';

        if (data.gifts.length === 0) {
            grid.innerHTML = '<div class="col-span-2 text-center text-hint py-10">No gifts found.</div>';
            return;
        }

        // Render Items
        data.gifts.forEach(gift => {
            const card = document.createElement('div');
            card.className = 'card overflow-hidden flex flex-col';

            // Image Placeholder (or real if we have it)
            // Ideally backend provides image URL
            const imgUrl = gift.image_url || 'https://via.placeholder.com/150/333/fff?text=Gift';

            // Construct the card HTML
            card.innerHTML = `
                <div class="aspect-square bg-gray-700 relative">
                     <img src="${imgUrl}" class="w-full h-full object-cover" onerror="this.src='https://via.placeholder.com/150?text=Error'">
                     <div class="absolute top-2 right-2 bg-black/50 backdrop-blur-md px-2 py-1 rounded-md text-xs font-mono">
                        #${gift.num || '?'}
                     </div>
                </div>
                <div class="p-3 flex-1 flex flex-col justify-between">
                    <div>
                        <h3 class="font-bold text-sm truncate">${gift.name}</h3>
                        <p class="text-xs text-hint truncate">${gift.details}</p>
                    </div>
                    <div class="mt-3 flex justify-between items-center">
                        <span class="text-lg font-bold text-blue-400">${gift.price > 0 ? gift.price : '-'}</span>
                        <span class="text-xs text-hint">TON</span>
                    </div>
                </div>
            `;

            grid.appendChild(card);
        });

    } catch (e) {
        console.error(e);
        // alert("Failed to load data");
        totalItemsEl.innerText = "Error loading data";
    }
}

function refreshData() {
    document.getElementById('total-value').innerText = '---';
    document.getElementById('gift-grid').innerHTML = `
        <div class="skeleton h-48 rounded-xl w-full"></div>
        <div class="skeleton h-48 rounded-xl w-full"></div>
    `;
    fetchPortfolio();
}

// Initial Load
// tg.ready();
fetchPortfolio();
