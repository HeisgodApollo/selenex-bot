import requests
import time

# === CONFIG ===
BOT_TOKEN = '8177484905:AAHnPeCWlYQYfoSklBLF_ktYOjaEzIuLXGE'
CHAT_ID = 6674319654  # Your Telegram ID

# === FILTERS ===
FILTERS = {
    'min_lp': 15000,
    'min_vol': 12000,
    'min_mc': 10000,
    'max_mc': 40000
}

# === TRENDING META TERMS ===
TREND_TERMS = [
    'elon', 'doge', 'shiba', 'pepe', 'floki', 'trump', 'maga', 'npc',
    'baby', 'moon', 'pump', 'wizard', 'jesus', 'chad', 'based', 'rekt',
    'degen', 'wagmi', 'gme', 'cat', 'toad', 'ape', 'banana', 'meme',
    'anime', 'waifu', 'sol', 'dino', 'frog', 'rat', 'zombie', 'phantom',
    'zoom', 'launch', 'airdrop', 'meta', 'ai', 'gpt', 'blast', 'nova',
    'quantum', 'cult', 'dark', 'angel', 'satoshi', 'wallet', 'matrix',
    'neo', 'oracle', 'tick', 'jeet', 'hold', 'bag', 'rizz', 'top', 'next',
    'gas', 'dump', 'rug', 'realest', 'liquidity'
]

# === TELEGRAM ALERT ===
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram send error:", e)

# === FETCH SOLANA COINS ===
def fetch_new_coins():
    url = 'https://public-api.birdeye.so/public/tokenlist?sort_by=volume_h24&sort_type=desc&offset=0&limit=50'
    headers = {
        'accept': 'application/json',
        'x-api-key': 'public'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            print("API error:", response.status_code)
            return []
    except Exception as e:
        print("Fetch error:", e)
        return []

# === META MATCHING ===
def matches_meta(name):
    name = name.lower()
    return any(term in name for term in TREND_TERMS)

# === FILTER CHECK ===
def passes_filters(coin):
    try:
        mc = float(coin.get("market_cap", 0))
        lp = float(coin.get("liquidity_usd", 0))
        vol = float(coin.get("volume_h24", 0))
        return (
            lp >= FILTERS['min_lp'] and
            vol >= FILTERS['min_vol'] and
            FILTERS['min_mc'] <= mc <= FILTERS['max_mc']
        )
    except Exception as e:
        print("Filter error:", e)
        return False

# === ALERT FORMAT + DEGEN SCORE ===
def alert_coin(coin):
    name = coin.get('name', 'N/A')
    symbol = coin.get('symbol', 'N/A')
    mc = float(coin.get('market_cap', 0))
    lp = float(coin.get('liquidity_usd', 0))
    vol = float(coin.get('volume_h24', 0))
    address = coin.get('address', '')
    chart_url = f"https://birdeye.so/token/{address}?chain=solana"

    # === DEGEN SCORE ===
    score = 0
    reasons = []

    if vol > 20000:
        score += 20
        reasons.append("High volume")

    if lp > 20000:
        score += 20
        reasons.append("Strong LP")

    if mc > 10000 and mc < 30000:
        score += 15
        reasons.append("Low MC range")

    if matches_meta(name) or matches_meta(symbol):
        score += 30
        reasons.append("Meta match")

    if lp > 0 and mc / lp < 5:
        score += 15
        reasons.append("Healthy LP/MC ratio")

    score = min(score, 100)

    # Emoji tags
    if score >= 85:
        tag = "🔥 VERY HOT"
    elif score >= 65:
        tag = "🚀 Moon Watch"
    elif score >= 40:
        tag = "⚠️ Semi Degen"
    else:
        tag = "🧊 Cold Entry"

    reason_str = " | ".join(reasons)

    # === TELEGRAM MESSAGE ===
    message = f"""
<b>🚀 Selenex SOL Alert!</b>

<b>Name</b>: {name} (${symbol})
<b>MC</b>: ${mc:,.0f} | <b>LP</b>: ${lp:,.0f} | <b>Vol</b>: ${vol:,.0f}

<b>DegenScore™</b>: <code>{score}/100</code> – {tag}
🧠 <i>{reason_str}</i>

🔗 <a href="{chart_url}">View on Birdeye</a>
"""
    send_message(message)

# === MAIN LOOP ===
def main():
    send_message("✅ Selenex (Solana-Only) is now active.")
    while True:
        coins = fetch_new_coins()
        print(f"Checking {len(coins)} Solana tokens...")

        for coin in coins:
            name = coin.get('name', '').lower()
            if matches_meta(name) and passes_filters(coin):
                print("🚨 MATCH:", name)
                alert_coin(coin)

        time.sleep(60)

if __name__ == "__main__":
    main()
