import requests
from bs4 import BeautifulSoup
import json
import os
import sys

URL = "https://www.huntercardtcg.com/categoria-producto/preventas/"
STATE_FILE = "products.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


def get_products() -> list[str]:
    r = requests.get(URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # WooCommerce genera títulos en estos selectores (en orden de prioridad)
    selectors = [
        "h2.woocommerce-loop-product__title",
        ".woocommerce-loop-product__title",
        "h2.product-title",
        ".product-title",
        "li.product h2",
        "li.product .woocommerce-LoopProduct-link",
    ]
    for sel in selectors:
        titles = soup.select(sel)
        if titles:
            return [t.get_text(strip=True) for t in titles]

    print("WARNING: no se encontraron selectores conocidos. HTML sample:")
    print(soup.find("ul", class_="products") or "no se encontró <ul.products>")
    return []


def load_known() -> list[str]:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_known(products: list[str]) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)


def notify_ntfy(topic: str, new_products: list[str]) -> None:
    body = "\n".join(f"• {p}" for p in new_products)
    try:
        r = requests.post(
            f"https://ntfy.sh/{topic}",
            data=body.encode("utf-8"),
            headers={
                "Title": f"🎴 {len(new_products)} nueva(s) preventa(s) en Hunter TCG",
                "Priority": "high",
                "Tags": "tada,shopping_cart",
                "Click": URL,
            },
            timeout=15,
        )
        r.raise_for_status()
        print(f"Notificación ntfy.sh enviada a tema '{topic}'")
    except Exception as e:
        print(f"ERROR ntfy.sh: {e}")


def notify_telegram(token: str, chat_id: str, new_products: list[str]) -> None:
    lines = "\n".join(f"• {p}" for p in new_products)
    msg = (
        f"🎴 <b>Nueva preventa en Hunter Card TCG</b>\n\n"
        f"{lines}\n\n"
        f'<a href="{URL}">Ver preventas →</a>'
    )
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"},
            timeout=15,
        )
        r.raise_for_status()
        print(f"Notificación Telegram enviada a chat {chat_id}")
    except Exception as e:
        print(f"ERROR Telegram: {e}")


def main() -> int:
    print(f"Revisando: {URL}")

    try:
        current = get_products()
    except Exception as e:
        print(f"ERROR al obtener productos: {e}")
        return 1

    print(f"Productos actuales ({len(current)}): {current or 'ninguno'}")

    known = load_known()
    new_products = [p for p in current if p not in known]
    removed = [p for p in known if p not in current]

    if new_products:
        print(f"NUEVOS: {new_products}")

        ntfy_topic = os.environ.get("NTFY_TOPIC", "").strip()
        if ntfy_topic:
            notify_ntfy(ntfy_topic, new_products)

        tg_token = os.environ.get("TELEGRAM_TOKEN", "").strip()
        tg_chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
        if tg_token and tg_chat:
            notify_telegram(tg_token, tg_chat, new_products)

        if not ntfy_topic and not tg_token:
            print("AVISO: no hay método de notificación configurado.")
    else:
        print("Sin cambios.")

    if removed:
        print(f"Ya no disponibles: {removed}")

    save_known(current)
    return 0


if __name__ == "__main__":
    sys.exit(main())
