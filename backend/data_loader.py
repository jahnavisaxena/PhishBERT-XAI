

import random
import pandas as pd
from datasets import load_dataset
from sklearn.model_selection import train_test_split

HOMOGLYPH_MAP = {
    'a': ['\u0430', '\u00e0', '\u00e1', '\u1ea1'],   # Cyrillic а, à, á, ạ
    'e': ['\u0435', '\u00e8', '\u00e9', '\u0117'],   # Cyrillic е, è, é, ė
    'o': ['\u043e', '\u00f2', '\u00f3', '\u01a1'],   # Cyrillic о, ò, ó, ơ
    'c': ['\u0441', '\u00e7', '\u0188'],             # Cyrillic с, ç, ƈ
    'p': ['\u0440', '\u03c1'],                       # Cyrillic р, Greek ρ
    'i': ['\u0456', '\u00ec', '\u00ed', '\u0131'],   # Cyrillic і, ì, í, ı
    's': ['\u0455', '\u015b', '\u0219'],             # Cyrillic ѕ, ś, ș
    'x': ['\u0445', '\u04b3'],                       # Cyrillic х, ҳ
    'y': ['\u0443', '\u00fd'],                       # Cyrillic у, ý
    'd': ['\u0501', '\u0257'],                       # Cyrillic ԁ, ɗ
    'g': ['\u0261', '\u01e5'],                       # ɡ, ǥ
    'h': ['\u04bb', '\u0570'],                       # Cyrillic һ, Armenian հ
    'k': ['\u043a'],                                 # Cyrillic к
    'l': ['\u006c', '\u0049', '\u04cf'],             # l, I, Cyrillic ӏ
    'n': ['\u0578'],                                 # Armenian ո
    'u': ['\u03c5', '\u057d'],                       # Greek υ, Armenian ս
    'w': ['\u051d'],                                 # Cyrillic ԝ
}

SEED_DOMAINS = [
    'google.com', 'facebook.com', 'apple.com', 'amazon.com',
    'microsoft.com', 'paypal.com', 'netflix.com', 'instagram.com',
    'twitter.com', 'linkedin.com', 'yahoo.com', 'github.com',
    'dropbox.com', 'spotify.com', 'adobe.com', 'slack.com',
    'zoom.us', 'chase.com', 'wellsfargo.com', 'bankofamerica.com',
    'citibank.com', 'hsbc.com', 'ebay.com', 'walmart.com',
    'target.com', 'bestbuy.com', 'reddit.com', 'twitch.tv',
    'discord.com', 'telegram.org', 'whatsapp.com', 'signal.org',
]


def generate_homoglyph(domain: str, num_subs: int = None) -> str:
    """
    Generate a homoglyph variant of a domain by substituting
    random characters with visually similar Unicode characters.
    """
    name = domain.split('.')[0]
    tld = '.'.join(domain.split('.')[1:])

    positions = [(i, ch) for i, ch in enumerate(name) if ch in HOMOGLYPH_MAP]
    if not positions:
        return domain  

    if num_subs is None:
        num_subs = random.randint(1, max(1, len(positions) // 2))
    num_subs = min(num_subs, len(positions))

    chosen = random.sample(positions, num_subs)
    chars = list(name)
    for idx, ch in chosen:
        chars[idx] = random.choice(HOMOGLYPH_MAP[ch])

    return ''.join(chars) + '.' + tld


def generate_homoglyph_samples(n: int = 5000) -> list:
    """Generate n homoglyph domain samples."""
    samples = []
    for _ in range(n):
        domain = random.choice(SEED_DOMAINS)
        homo = generate_homoglyph(domain)
        if homo != domain: 
            samples.append(homo)
    return samples


def load_and_split_data(sample_size=None):
    """
    Loads data from two sources and creates a 3-class dataset.

    Returns:
        (X_train, y_train), (X_val, y_val), (X_test, y_test)
    """
    print("Loading phishing URL dataset from HuggingFace (Mitake/PhishingURLsANDBenignURLs)...")
    dataset = load_dataset("Mitake/PhishingURLsANDBenignURLs")
    df = dataset['train'].to_pandas()

    print(f"Raw dataset shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"Label distribution: {df['label'].value_counts().to_dict()}")

    df_safe = df[df['label'] == 0].copy()
    df_phish = df[df['label'] == 1].copy()

    if sample_size:
        per_class = sample_size // 3
        df_safe = df_safe.sample(n=min(per_class, len(df_safe)), random_state=42)
        df_phish = df_phish.sample(n=min(per_class, len(df_phish)), random_state=42)
        n_homo = per_class
    else:
        n_per_class = min(len(df_safe), len(df_phish), 50000)
        df_safe = df_safe.sample(n=n_per_class, random_state=42)
        df_phish = df_phish.sample(n=n_per_class, random_state=42)
        n_homo = n_per_class

    print(f"Generating {n_homo} homoglyph domain samples...")
    homo_urls = generate_homoglyph_samples(n=n_homo)

    urls = (
        df_safe['url'].astype(str).tolist() +
        homo_urls +
        df_phish['url'].astype(str).tolist()
    )
    labels = (
        [0] * len(df_safe) +
        [1] * len(homo_urls) +
        [2] * len(df_phish)
    )

    print(f"Combined dataset: {len(urls)} samples")
    print(f"  Safe: {len(df_safe)}, Homograph: {len(homo_urls)}, Phishing: {len(df_phish)}")

    X_train, X_temp, y_train, y_temp = train_test_split(
        urls, labels, test_size=0.3, random_state=42, stratify=labels
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
    )

    print(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
    return (X_train, y_train), (X_val, y_val), (X_test, y_test)


if __name__ == "__main__":
    (X_train, y_train), (X_val, y_val), (X_test, y_test) = load_and_split_data(sample_size=300)
    print(f"\nTrain size: {len(X_train)}, Val size: {len(X_val)}, Test size: {len(X_test)}")
    print(f"Sample Safe: {X_train[y_train.index(0) if 0 in y_train else 0]}")
    homo_idx = y_train.index(1) if 1 in y_train else 0
    try:
        print(f"Sample Homograph: {X_train[homo_idx].encode('utf-8').decode('utf-8')}")
    except Exception:
        print(f"Sample Homograph: [contains Unicode chars, cannot display in this console]")
    phish_idx = y_train.index(2) if 2 in y_train else 0
    print(f"Sample Phishing: {X_train[phish_idx]}")
