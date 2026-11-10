import hashlib
import os
import struct

VAULT_KEY_WORDS = [
    0xB501996D,
    0x7F4A7C15,
    0x0666DAEE,
    0x513C0DE9,
    0xA5C39E21,
    0x38D1F4B2,
    0xC90FDAA2,
    0xE47B1337,
]

NUM_SHARDS = 4


def keystream_word(word_index: int) -> int:
    z = (word_index + 0x9E3779B9) & 0xFFFFFFFF
    z = ((z ^ (z >> 16)) * 0x85EBCA6B) & 0xFFFFFFFF
    z = ((z ^ (z >> 13)) * 0xC2B2AE35) & 0xFFFFFFFF
    z = (z ^ (z >> 16) ^ VAULT_KEY_WORDS[word_index & 7]) & 0xFFFFFFFF
    return z


def transform_chunk(raw_bytes: bytes, global_byte_offset: int) -> bytes:
    assert global_byte_offset % 4 == 0
    start_word = global_byte_offset // 4
    n_words = len(raw_bytes) // 4
    rem = len(raw_bytes) % 4

    out = bytearray(len(raw_bytes))
    words = struct.unpack_from(f"<{n_words}I", raw_bytes, 0)
    enc_words = [w ^ keystream_word(start_word + i) for i, w in enumerate(words)]
    struct.pack_into(f"<{n_words}I", out, 0, *enc_words)

    if rem > 0:
        kw = keystream_word(start_word + n_words)
        base = n_words * 4
        for b in range(rem):
            out[base + b] = raw_bytes[base + b] ^ ((kw >> (b * 8)) & 0xFF)

    return bytes(out)


def main():
    src_path = r"C:\Users\Daniel Sawitzki\Desktop\BF_History.mp4"
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    vault_dir = os.path.join(repo_root, "assets", "vault")
    os.makedirs(vault_dir, exist_ok=True)

    with open(src_path, "rb") as f:
        src_data = f.read()

    total_len = len(src_data)
    src_sha256 = hashlib.sha256(src_data).hexdigest()
    print(f"Source BF_History.mp4: {total_len} bytes, SHA256={src_sha256}")

    # Align shard boundaries to 4-byte multiples
    raw_shard_size = ((total_len // NUM_SHARDS) + 3) & ~3

    reassembled = bytearray()
    offset = 0
    for idx in range(NUM_SHARDS):
        end = total_len if idx == NUM_SHARDS - 1 else min(total_len, offset + raw_shard_size)
        chunk = src_data[offset:end]
        enc = transform_chunk(chunk, offset)
        shard_path = os.path.join(vault_dir, f"b50_reel_{idx:02d}.bin")
        with open(shard_path, "wb") as sf:
            sf.write(enc)
        print(f"  Wrote {shard_path} ({len(enc)} bytes, offset={offset})")

        # Round-trip verify
        dec = transform_chunk(enc, offset)
        reassembled.extend(dec)
        offset = end

    dec_sha256 = hashlib.sha256(reassembled).hexdigest()
    assert dec_sha256 == src_sha256, "Decryption roundtrip mismatch!"
    print(f"Verified round-trip SHA256 match ({len(reassembled)} bytes).")


if __name__ == "__main__":
    main()

