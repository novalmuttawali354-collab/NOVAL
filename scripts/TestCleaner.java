import com.antokon.pkmobile.TextCleaner;

public class TestCleaner {
    private static void check(String raw, String expected) {
        String clean = TextCleaner.clean(raw);
        if (TextCleaner.dirty(clean)) {
            throw new RuntimeException("DIRTY: " + clean);
        }
        if (!clean.equals(expected)) {
            throw new RuntimeException("EXPECTED=[" + expected + "] GOT=[" + clean + "]");
        }
        System.out.println("CLEAN_OK: " + clean.replace("\n", " | "));
    }

    public static void main(String[] args) {
        check(
            "text#macro:<HTML><HEAD><META content=\"text/html; charset=unicode\" http-equiv=Content-Type><META name=GENERATOR content=\"MSHTML 11.00.10570.1001\"></HEAD><BODY>Mohon maaf setelah kami cekkan akun ewallet anda sudah melebihi batas limit bulanan ya bosku <BR>mohon anda berikan nomor rekening bank anda agar bisa kami bantu proseskan Wihtdraw anda ya bosku </BODY></HTML>",
            "Mohon maaf setelah kami cekkan akun ewallet anda sudah melebihi batas limit bulanan ya bosku\nmohon anda berikan nomor rekening bank anda agar bisa kami bantu proseskan Wihtdraw anda ya bosku"
        );

        check(
            "text#macro:<HTML><HEAD><META content=\"text/html; charset=unicode\" http-equiv=Content-Type><META name=GENERATOR content=\"MSHTML 11.00.10570.1001\"></HEAD><BODY>mohon maaf ya bosku akun anda di lock otomatis oleh system dikarenakan nomor rekening anda tidak valid ya bosku</BODY></HTML>",
            "mohon maaf ya bosku akun anda di lock otomatis oleh system dikarenakan nomor rekening anda tidak valid ya bosku"
        );
    }
}
