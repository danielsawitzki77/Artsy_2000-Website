import hashlib
import json
import os
import struct

NUM_SHARDS = 4


def load_vault_key_words(repo_root: str) -> list[int]:
    """Load the 8 x uint32 vault stream key words from B50_VAULT_KEY or untracked .vault_key.json."""
    env_val = os.environ.get("B50_VAULT_KEY", "").strip()
    if env_val:
        parts = [p.strip() for p in env_val.split(",") if p.strip()]
        if len(parts) != 8:
            raise ValueError("B50_VAULT_KEY must contain 8 comma-separated 32-bit integers.")
        return [int(p, 0) & 0xFFFFFFFF for p in parts]

    key_file = os.path.join(repo_root, ".vault_key.json")
    if not os.path.exists(key_file):
        raise FileNotFoundError(
            f"Missing local key file '{key_file}' and B50_VAULT_KEY env var is not set."
        )
    with open(key_file, "r", encoding="utf-8") as kf:
        data = json.load(kf)
    words = data.get("vault_key_words", [])
    if len(words) != 8:
        raise ValueError(".vault_key.json 'vault_key_words' must contain 8 32-bit integers.")
    return [(int(w, 0) if isinstance(w, str) else int(w)) & 0xFFFFFFFF for w in words]


def keystream_word(word_index: int, vault_key_words: list[int]) -> int:
    z = (word_index + 0x9E3779B9) & 0xFFFFFFFF
    z = ((z ^ (z >> 16)) * 0x85EBCA6B) & 0xFFFFFFFF
    z = ((z ^ (z >> 13)) * 0xC2B2AE35) & 0xFFFFFFFF
    z = (z ^ (z >> 16) ^ vault_key_words[word_index & 7]) & 0xFFFFFFFF
    return z


def transform_chunk(raw_bytes: bytes, global_byte_offset: int, vault_key_words: list[int]) -> bytes:
    assert global_byte_offset % 4 == 0
    start_word = global_byte_offset // 4
    n_words = len(raw_bytes) // 4
    rem = len(raw_bytes) % 4

    out = bytearray(len(raw_bytes))
    words = struct.unpack_from(f"<{n_words}I", raw_bytes, 0)
    enc_words = [w ^ keystream_word(start_word + i, vault_key_words) for i, w in enumerate(words)]
    struct.pack_into(f"<{n_words}I", out, 0, *enc_words)

    if rem > 0:
        kw = keystream_word(start_word + n_words, vault_key_words)
        base = n_words * 4
        for b in range(rem):
            out[base + b] = raw_bytes[base + b] ^ ((kw >> (b * 8)) & 0xFF)

    return bytes(out)


def main():
    src_path = os.environ.get("B50_VAULT_SRC_MP4", r"C:\Users\Daniel Sawitzki\Desktop\BF_History.mp4")
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    vault_key_words = load_vault_key_words(repo_root)
    vault_dir = os.path.join(repo_root, "assets", "vault")
    os.makedirs(vault_dir, exist_ok=True)

    with open(src_path, "rb") as f:
        src_data = f.read()

    total_len = len(src_data)
    src_sha256 = hashlib.sha256(src_data).hexdigest()
    print(f"Source MP4: {total_len} bytes, SHA256={src_sha256}")

    # Align shard boundaries to 4-byte multiples
    raw_shard_size = ((total_len // NUM_SHARDS) + 3) & ~3

    reassembled = bytearray()
    offset = 0
    for idx in range(NUM_SHARDS):
        end = total_len if idx == NUM_SHARDS - 1 else min(total_len, offset + raw_shard_size)
        chunk = src_data[offset:end]
        enc = transform_chunk(chunk, offset, vault_key_words)
        shard_path = os.path.join(vault_dir, f"b50_reel_{idx:02d}.bin")
        with open(shard_path, "wb") as sf:
            sf.write(enc)
        print(f"  Wrote {shard_path} ({len(enc)} bytes, offset={offset})")

        # Round-trip verify
        dec = transform_chunk(enc, offset, vault_key_words)
        reassembled.extend(dec)
        offset = end

    dec_sha256 = hashlib.sha256(reassembled).hexdigest()
    assert dec_sha256 == src_sha256, "Decryption roundtrip mismatch!"
    print(f"Verified round-trip SHA256 match ({len(reassembled)} bytes).")


if __name__ == "__main__":
    main()
