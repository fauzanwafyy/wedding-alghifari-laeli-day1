/**
 * ============================================================================
 *  WEDDING CONFIGURATION: the ONE file to edit for wedding content.
 *  Resepsi Pernikahan Alghifari & Laeli · Day 1 · 20 Oktober 2026
 * ============================================================================
 *
 *  Edit the values below, save, commit and push. GitHub Pages redeploys
 *  automatically (about 1 minute). See docs/MAINTENANCE.md for step-by-step help.
 *
 *  Rules of thumb
 *  - Keep the quotes "..." around text. Use \n for a line break inside text.
 *  - Dates/times are ISO strings WITH the +07:00 (WIB) offset, e.g.
 *    "2026-10-20T09:00:00+07:00". This keeps the countdown correct for guests
 *    in any timezone.
 *  - The <head> of index.html (page title / WhatsApp preview text) is static.
 *    If you change the couple's names or the date, update it there too.
 * ============================================================================
 */

const WEDDING_CONFIG = {
  /* --------------------------------------------------------------------- *
   *  SITE
   * --------------------------------------------------------------------- */
  site: {
    // Public URL of the invitation (used in the calendar description and the
    // guest-link generator). Leave "" to auto-detect from the browser address.
    url: "https://day1.onepercent.my.id/",
    locale: "id-ID",
  },

  /* --------------------------------------------------------------------- *
   *  PAGE PHOTOS: cover, header and closing.
   *  All photos are listed in this file (couple portraits below, story and
   *  gallery further down). See docs/PHOTO-REPLACEMENT-GUIDE.md.
   *  `position` = which part of the photo stays visible when it is cropped
   *  ("50% 40%" = horizontally centred, slightly above the middle).
   * --------------------------------------------------------------------- */
  images: {
    // Opening cover (first screen) · source: cover/cover.jpg
    cover: {
      src: "assets/images/cover/cover", widths: [640, 960, 1440], w: 5888, h: 8832, color: "#8d9b85",
      position: "42% 66%", positionDesktop: "45% 62%",
      alt: "Laeli bersandar di bahu Alghifari di atas bangku kayu di taman",
    },
    // Header after opening · source: cover/header.jpg
    hero: {
      src: "assets/images/cover/hero", widths: [640, 960, 1440], w: 5888, h: 8832, color: "#495b39",
      position: "58% 50%", positionDesktop: "50% 58%",
      alt: "Alghifari dan Laeli berjalan bergandengan di antara bunga kosmos",
    },
    // Closing "Terima Kasih" section · source: cover/footer.jpg
    closing: {
      src: "assets/images/cover/closing", widths: [640, 960, 1440], w: 2797, h: 4195, color: "#918b7d",
      position: "62% 52%",
      alt: "Alghifari dan Laeli melangkah bergandengan dari teras rumah putih",
    },
  },


  /* --------------------------------------------------------------------- *
   *  COUPLE & PARENTS
   * --------------------------------------------------------------------- */
  couple: {
    groom: {
      fullName: "MOH AGIL ALGHIFARI",        // official name (as provided)
      displayName: "Moh Agil Alghifari",     // how it is typeset on the page
      nickname: "Alghifari",                 // used in "Alghifari & Laeli"
      initial: "A",
      childOf: "Putra Pertama dari",
      father: { prefix: "Bapak", name: "H. Lukmanudin" },
      mother: { prefix: "Ibu", name: "Atik" },
      instagram: "",                         // e.g. "username" (without @). Empty = hidden.
      photo: {
        src: "assets/images/groom/groom",              // source: groom/groom.jpeg
        widths: [480, 800, 1200], w: 1365, h: 2048, color: "#6e7150", position: "50% 22%",
        alt: "Potret Moh Agil Alghifari mengenakan busana berwarna taupe",
      },
    },
    bride: {
      fullName: "LAELI LUSPITASARI",
      displayName: "Laeli Luspitasari",
      nickname: "Laeli",
      initial: "L",
      childOf: "Putri Ketiga dari",
      father: { prefix: "Bapak", name: "Misbah Hidayat" },
      mother: { prefix: "Ibu", name: "Iin Suryani" },
      instagram: "",
      photo: {
        src: "assets/images/bride/bride",              // source: bride/bride.jpeg
        widths: [480, 800, 1200], w: 1365, h: 2048, color: "#77855d", position: "50% 24%",
        alt: "Potret Laeli Luspitasari menggenggam buket bunga putih",
      },
    },
  },

  /* --------------------------------------------------------------------- *
   *  DATE & COUNTDOWN
   * --------------------------------------------------------------------- */
  wedding: {
    date: "2026-10-20",
    timezone: "Asia/Jakarta",
    timezoneLabel: "WIB",
    // The countdown counts down to this moment (first event start).
    countdownTarget: "2026-10-20T09:00:00+07:00",
    // After the countdown reaches zero the page shows the "today" message
    // until this moment, then the "after" message (end of the reception).
    celebrationEnds: "2026-10-20T21:00:00+07:00",
  },

  /* --------------------------------------------------------------------- *
   *  VENUE
   * --------------------------------------------------------------------- */
  venue: {
    name: "Le Villa Resort and Conference",
    address: "Jl. Lembah Nyiur No.46, Kopo, Kec. Cisarua, Kabupaten Bogor, Jawa Barat 16750",
    shortAddress: "Kopo, Cisarua, Kabupaten Bogor",
    mapsUrl: "https://goo.gl/maps/DwpyJcmFjXAfgyxz6",
  },

  /* --------------------------------------------------------------------- *
   *  EVENTS: one card per event.
   *  endTime: "HH:MM" or null.  endText: shown after the start time when
   *  endTime is null (e.g. "selesai" → "10.00 WIB – selesai").
   * --------------------------------------------------------------------- */
  events: [
    {
      title: "Resepsi",
      date: "2026-10-20",
      startTime: "09:00",
      endTime: "21:00",
      endText: "",
      timezone: "Asia/Jakarta",
      venue: "Le Villa Resort and Conference",
      address: "Jl. Lembah Nyiur No.46, Kopo, Kec. Cisarua, Kabupaten Bogor, Jawa Barat 16750",
      mapsUrl: "https://goo.gl/maps/DwpyJcmFjXAfgyxz6",
      note: "",
    },
  ],

  /* --------------------------------------------------------------------- *
   *  SAVE THE DATE (Google Calendar)
   *  The "Simpan ke Kalender" buttons save the reception, 09.00–21.00 WIB.
   * --------------------------------------------------------------------- */
  calendar: {
    title: "Resepsi Pernikahan Alghifari & Laeli",
    eventTitleSuffix: " · Alghifari & Laeli",   // per-event entries: "Resepsi · Alghifari & Laeli"
    location: "",                                // empty = venue.name + venue.address (above)
    description:
      "Dengan penuh rasa syukur, kami mengundang Bapak/Ibu/Saudara/i untuk hadir dan memberikan doa restu pada acara resepsi pernikahan kami.",
  },

  /* --------------------------------------------------------------------- *
   *  OUR STORY: four chapters. Text is preserved from the brief.
   * --------------------------------------------------------------------- */
  story: [
    {
      number: "01",
      title: "Pertemuan",
      paragraphs: [
        "Tidak ada yang benar-benar terjadi secara kebetulan di dunia ini. Segalanya telah tersusun rapi oleh Sang Maha Kuasa, termasuk tentang kepada siapa hati ini akhirnya memilih untuk jatuh cinta.",
        "Hari itu, tanpa pernah kita duga sebelumnya, kita dipertemukan di tempat yang sama, dalam satu pekerjaan. Sebuah pertemuan sederhana yang saat itu mungkin terasa biasa saja, namun ternyata menjadi awal dari perjalanan panjang yang membawa kita sampai sejauh ini.",
      ],
      image: {
        src: "assets/images/story/story-01", widths: [480, 800, 1200], w: 5713, h: 8570, color: "#777850", position: "56% 62%", // source: cover/pertemuan.jpg
        alt: "Alghifari dan Laeli berdiri di jembatan batu di tepi aliran sungai",
      },
    },
    {
      number: "02",
      title: "Pendekatan",
      paragraphs: [
        "Seiring berjalannya waktu, katanya cinta dapat tumbuh dari kebersamaan. Dari obrolan-obrolan kecil yang sederhana, perlahan tumbuh rasa nyaman yang membuat kami ingin saling mengenal lebih jauh.",
        "Hingga beberapa bulan kemudian, tanpa banyak rencana yang rumit, kami memutuskan untuk melangkah bersama dalam sebuah hubungan. Dari situlah, cerita kami perlahan dimulai.",
      ],
      image: {
        src: "assets/images/story/story-02", widths: [480, 800, 1200], w: 5888, h: 8832, color: "#8da57e", position: "62% 40%", // source: cover/pendekatan.jpg
        alt: "Alghifari dan Laeli tersenyum di tengah rerumputan hijau",
      },
    },
    {
      number: "03",
      title: "Lamaran",
      paragraphs: [
        "Perjalanan kami tentu bukan tanpa ujian dan cerita. Ada banyak hal yang harus kami lewati, ada jalan yang tidak selalu mudah, dan ada waktu-waktu yang mengajarkan kami tentang kesabaran.",
        "Namun, setiap proses yang kami lalui justru membuat kami semakin mengenal, memahami, dan menguatkan satu sama lain. Hingga pada akhirnya, kami semakin yakin bahwa perjalanan ini layak untuk diperjuangkan bersama.",
      ],
      image: {
        src: "assets/images/story/story-03", widths: [480, 800, 1200], w: 5140, h: 7710, color: "#71845a", position: "50% 64%", // source: cover/lamaran.jpg
        alt: "Alghifari dan Laeli saling berhadapan menggenggam buket bunga",
      },
    },
    {
      number: "04",
      title: "Pernikahan",
      paragraphs: [
        "Kami percaya, bukan karena bertemu lalu berjodoh, tetapi karena berjodohlah Allah SWT mempertemukan kami dengan cara terbaik-Nya.",
        "Dengan rasa penuh syukur, kami memutuskan untuk mengikrarkan janji suci pernikahan pada tanggal 21 Oktober 2026.",
        "Kami mengerti, bukan semua jalan akan berjalan dengan mudah, dan tidak setiap doa dijawab secepat yang kita harapkan. Namun, di setiap jeda, kami belajar untuk percaya kepada Sang Maha Cinta, yang selalu tahu ke mana hati ini harus pulang.",
        "Hari ini, kami siap untuk melangkah lebih jauh, bersama.",
      ],
      image: {
        src: "assets/images/story/story-04", widths: [480, 800, 1200], w: 5888, h: 8832, color: "#565a37", position: "50% 62%", // source: cover/pernikahan.jpg
        alt: "Alghifari dan Laeli berdiri di jembatan kayu di bawah rimbun pakis",
      },
    },
  ],

  /* --------------------------------------------------------------------- *
   *  GALLERY: regular grid. Order = display order.
   *  gallery-01 … gallery-08 = gallery/galeri (1) … (8).jpg
   *  `wide: true` = landscape photo (full row on phones, two columns on tablet/desktop).
   * --------------------------------------------------------------------- */
  gallery: [
    { src: "assets/images/gallery/gallery-01", widths: [480, 800, 1600], w: 2944, h: 4416, color: "#856745", alt: "Alghifari dan Laeli berdiri di depan rumah joglo berukir kayu" },
    { src: "assets/images/gallery/gallery-02", widths: [480, 800, 1600], w: 2784, h: 4176, color: "#66552b", alt: "Alghifari dan Laeli di teras rumah joglo, terlihat di balik dedaunan" },
    { src: "assets/images/gallery/gallery-03", widths: [480, 800, 1600], w: 2944, h: 4416, color: "#997a57", alt: "Alghifari dan Laeli berdiri berdampingan di depan pintu rumah joglo" },
    { src: "assets/images/gallery/gallery-04", widths: [480, 800, 1600], w: 2944, h: 4416, color: "#8d7653", alt: "Laeli dan Alghifari berdiri di beranda kayu rumah joglo" },
    { src: "assets/images/gallery/gallery-05", widths: [480, 800, 1600], w: 3949, h: 5923, color: "#382608", alt: "Alghifari dan Laeli membawa lentera di tengah hutan pada malam hari" },
    { src: "assets/images/gallery/gallery-06", widths: [480, 800, 1600], w: 4160, h: 6240, color: "#391f02", alt: "Alghifari dan Laeli mengangkat lentera di bawah pepohonan pada malam hari" },
    { src: "assets/images/gallery/gallery-07", widths: [480, 800, 1600], w: 5888, h: 8832, color: "#44532f", alt: "Alghifari dan Laeli berdiri di padang rumput di depan bangunan beratap genteng" },
    { src: "assets/images/gallery/gallery-08", widths: [800, 1600, 2400], w: 8832, h: 5888, color: "#40502c", alt: "Alghifari dan Laeli berjalan di padang rumput hijau", wide: true },
  ],

  /* --------------------------------------------------------------------- *
   *  WEDDING GIFT
   *  accountNumber: digits only (spaces are added automatically on screen).
   * --------------------------------------------------------------------- */
  gift: {
    intro:
      "Bagi Bapak/Ibu/Saudara/i yang ingin mengirimkan hadiah pernikahan dapat melalui transfer bank di bawah ini :",
    accounts: [
      { label: "The Groom", bank: "BCA", accountNumber: "7361529751", accountHolder: "MOH AGIL ALGHIFARI" },
      { label: "The Bride", bank: "BCA", accountNumber: "7361504589", accountHolder: "LAELI LUSPITA SARI" },
    ],
  },

  /* --------------------------------------------------------------------- *
   *  RSVP & WEDDING WISHES (Google Apps Script backend)
   *  Same spreadsheet and Web App URL as the Day 2 invitation; Day 1's
   *  RSVPs go to their own tab ("RSVP Day 1") because of `event` below.
   *  See docs/GOOGLE-SHEETS.md.
   * --------------------------------------------------------------------- */
  rsvp: {
    apiUrl: "https://script.google.com/macros/s/AKfycbxAJ-qHfMK--DcGSp1C_9E1wrarz_hrWl2teccNZPfjWnxheVE5KCtGyzRTmHYj-7gm/exec",
    event: "day1",                // tab "RSVP Day 1" in the shared spreadsheet (see EVENTS in Code.gs)
    closed: false,                // true = stop accepting RSVPs (wishes stay visible)
    maxGuests: 5,                 // max people per RSVP (including the guest)
    nameMaxLength: 80,
    messageMaxLength: 500,
    requestTimeoutMs: 15000,
    wishesPollIntervalMs: 30000,  // refresh wishes every 30 s while visible
    wishesPageSize: 8,            // wishes shown before "show more"
  },

  /* --------------------------------------------------------------------- *
   *  MUSIC
   * --------------------------------------------------------------------- */
  music: {
    enabled: true,
    src: "assets/audio/wedding-song.mp3",
    title: "Bernaung · Feby Putri",
    volume: 0.7,
  },

  /* --------------------------------------------------------------------- *
   *  COPY: editable sentences used around the page
   * --------------------------------------------------------------------- */
  copy: {
    coverTo: "Kepada Yth. Bapak/Ibu/Saudara/i",
    coverDefaultGuest: "Tamu Undangan",
    coverNote: "Mohon maaf apabila ada kesalahan penulisan nama dan gelar.",
    openButton: "Buka Undangan",

    salam: "Assalamu’alaikum Warahmatullahi Wabarakatuh",
    intro:
      "Dengan memohon rahmat dan ridho Allah SWT, kami bermaksud mengundang Bapak/Ibu/Saudara/i untuk hadir dan memberikan doa restu pada acara resepsi pernikahan kami.",

    verse: {
      enabled: true,
      text: "Dan di antara tanda-tanda (kebesaran)-Nya ialah Dia menciptakan pasangan-pasangan untukmu dari jenismu sendiri, agar kamu cenderung dan merasa tenteram kepadanya, dan Dia menjadikan di antaramu rasa kasih dan sayang. Sungguh, pada yang demikian itu benar-benar terdapat tanda-tanda (kebesaran Allah) bagi kaum yang berpikir.",
      source: "QS. Ar-Rum : 21",
    },

    coupleIntro:
      "Maha Suci Allah yang telah menciptakan makhluk-Nya berpasang-pasangan. Atas rahmat dan ridho-Nya, kami dipersatukan dalam ikatan pernikahan.",

    countdownLabels: { days: "Hari", hours: "Jam", minutes: "Menit", seconds: "Detik" },
    countdownToday: "Hari bahagia telah tiba.",
    countdownTodaySub: "Resepsi berlangsung hari ini, pukul 09.00 – 21.00 WIB. Kami menanti kehadiran Anda.",
    countdownAfter: "Alhamdulillah.",
    countdownAfterSub: "Terima kasih atas kehadiran serta doa restu yang telah Anda berikan.",

    storyIntro: "Sebuah perjalanan sederhana, dari pertemuan yang tak direncanakan hingga janji yang kami ikrarkan.",
    galleryIntro: "Potongan waktu yang ingin kami simpan dan bagikan bersama Anda.",

    rsvpIntro:
      "Kehadiran dan doa restu Anda adalah hadiah terindah bagi kami. Mohon konfirmasi kehadiran melalui formulir berikut.",
    rsvpDeadline: "",            // e.g. "Mohon konfirmasi sebelum 14 Oktober 2026." Empty = hidden.
    rsvpClosed: "Konfirmasi kehadiran telah ditutup. Terima kasih atas doa dan perhatiannya.",

    wishesIntro: "Untaian doa dan ucapan dari keluarga, sahabat, dan orang-orang terkasih.",

    closing:
      "Merupakan suatu kehormatan dan kebahagiaan bagi kami apabila Bapak/Ibu/Saudara/i berkenan hadir dan memberikan doa restu kepada kami.",
    closingSalam: "Wassalamu’alaikum Warahmatullahi Wabarakatuh",
    closingSignature: "Kami yang berbahagia",
    familyPrefix: "Keluarga Besar",
  },
};

/* ============================================================================
 *  GUEST LIST (optional)
 *
 *  Two ways to personalise a link. Both work at the same time:
 *
 *  1) Free text, no setup needed:
 *       https://…/?to=Pujo                 → "Pujo"
 *       https://…/?to=Pujo+%26+Partner     → "Pujo & Partner"
 *
 *  2) Short slug from this list:
 *       https://…/?to=fauzan-wafi          → "Fauzan Wafi & Partner"
 *
 *  Keys must be lowercase-with-dashes. `partner` can be "Partner",
 *  "Keluarga", a real name, or "" for none. Use generator.html to create links.
 *  NOTE: this file is public, so only add what you're happy to be visible.
 * ========================================================================== */
const GUESTS = {
  "fauzan-wafi": { name: "Fauzan Wafi", partner: "Partner" },
  "ade-fitriyani": { name: "Ade Fitriyani", partner: "" },
};

// Make the configuration available to the other scripts.
window.WEDDING_CONFIG = WEDDING_CONFIG;
window.GUESTS = GUESTS;
