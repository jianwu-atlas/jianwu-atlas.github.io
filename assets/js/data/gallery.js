const galleryData = [
  /* ─── 影片（Films）—— 同一部片多平台合一：一张卡内含 YouTube + Bilibili 两个入口 ─── */
  {
    type: "video",
    category: "Films",
    date: "2026-10-12",
    caption: "吴坚 & 肖维 婚礼蜜月影片｜婚礼 · 蜜月 · 4K",
    thumb: "assets/img/gallery/thumbs/wedding-honeymoon-cover.webp",
    sources: [
      { source: "youtube",  src: "https://www.youtube.com/embed/COaOpLmc_iQ?start=0" },
      { source: "bilibili", src: "https://player.bilibili.com/player.html?bvid=BV1L3p46FEDE&page=1&high_quality=1&danmaku=0" }
    ]
  },
  {
    type: "video",
    category: "Films",
    date: "2026-10-12",
    caption: "吴坚 & 肖维 婚礼影片｜WEDDING DAY · 4K",
    thumb: "assets/img/gallery/thumbs/wedding-day-cover.webp",
    sources: [
      { source: "youtube",  src: "https://www.youtube.com/embed/2d-WzuMwpW0?start=0" },
      { source: "bilibili", src: "https://player.bilibili.com/player.html?bvid=BV1CJHd6pEdx&page=1&high_quality=1&danmaku=0" }
    ]
  },
  {
    type: "video",
    category: "Films",
    date: "2026-10-12",
    caption: "吴坚 & 肖维 蜜月影片｜蜜月 · 大理 · 4K",
    thumb: "assets/img/gallery/thumbs/honeymoon-dali-cover.webp",
    sources: [
      { source: "youtube",  src: "https://www.youtube.com/embed/iWVSWx9Ctc8?start=0" },
      { source: "bilibili", src: "https://player.bilibili.com/player.html?bvid=BV1xjHd6xEHR&page=1&high_quality=1&danmaku=0" }
    ]
  },

  /* ─── 科研照片（Research · 本地 assets/img/gallery/） ─── */
  { type: "photo", thumb: "assets/img/gallery/thumbs/photo1.webp", category: "Research", date: "2026-07-07", source: "local", src: "assets/img/gallery/photo1.jpg", caption: "Jian Wu" },
  // 下面几张暂时没有实际文件，先注释掉，以后补上照片再取消注释
  // { type: "photo", category: "Research", date: "2026-07-07", source: "local", src: "assets/img/gallery/photo2.jpg", caption: "Lab life" },
  // { type: "photo", category: "Research", date: "2026-07-07", source: "local", src: "assets/img/gallery/photo3.jpg", caption: "Conference trip" },
  // { type: "photo", category: "Research", date: "2026-07-07", source: "local", src: "assets/img/gallery/photo4.jpg", caption: "Nature walk" },

  { type: "photo", thumb: "assets/img/gallery/thumbs/2024-03-05-CIGL_party-合照.webp", category: "Research", date: "2024-03-05", source: "local", src: "assets/img/gallery/2024-03-05-CIGL_party-合照.jpeg", caption: "CIGL Party · 2024-03-05" },

  { type: "photo", thumb: "assets/img/gallery/thumbs/2024-12-14--单独Soni.webp", category: "Research", date: "2024-12-14", source: "local", src: "assets/img/gallery/2024-12-14--单独Soni.jpeg", caption: "与 Prof. Soni Savai Pullamsetti 合影 · 2024-12-14" },

  { type: "photo", thumb: "assets/img/gallery/thumbs/2024-12-14-合照2-X.webp", category: "Research", date: "2024-12-14", source: "local", src: "assets/img/gallery/2024-12-14-合照2-X.jpeg", caption: "团队合照 · 2024-12-14" },

  { type: "photo", thumb: "assets/img/gallery/thumbs/CPI会议.webp", category: "Research", date: "2023-09-25", source: "local", src: "assets/img/gallery/CPI会议.jpeg", caption: "CPI 会议" },

  { type: "photo", thumb: "assets/img/gallery/thumbs/CRC Retreat 2025.webp", category: "Research", date: "2025-03-28", source: "local", src: "assets/img/gallery/CRC Retreat 2025.jpg", caption: "CRC Retreat 2025" },

  { type: "photo", thumb: "assets/img/gallery/thumbs/DataLung 2026 合照.webp", category: "Research", date: "2026-05-12", source: "local", src: "assets/img/gallery/DataLung 2026 合照.jpeg", caption: "DataLung 2026 合照" },

  { type: "photo", thumb: "assets/img/gallery/thumbs/DZL 2024 合照.webp", category: "Research", date: "2024-07-05", source: "local", src: "assets/img/gallery/DZL 2024 合照.jpg", caption: "DZL 2024 合照" },

  { type: "photo", thumb: "assets/img/gallery/thumbs/DZL 2025合照.webp", category: "Research", date: "2025-07-31", source: "local", src: "assets/img/gallery/DZL 2025合照.jpg", caption: "DZL 2025 合照" },

  { type: "photo", thumb: "assets/img/gallery/thumbs/DZL2026-合照.webp", category: "Research", date: "2026-06-22", source: "local", src: "assets/img/gallery/DZL2026-合照.jpg", caption: "DZL 2026 合照" },

  { type: "photo", thumb: "assets/img/gallery/thumbs/ILH Symposium 2025.webp", category: "Research", date: "2025-03-28", source: "local", src: "assets/img/gallery/ILH Symposium 2025.jpeg", caption: "ILH Symposium 2025" },

  { type: "photo", thumb: "assets/img/gallery/thumbs/Image from CPI 2.0 合照.webp", category: "Research", date: "2026-07-07", source: "local", src: "assets/img/gallery/Image from CPI 2.0 合照.png", caption: "CPI 2.0 团队合照" },

  /* ─── 生活视频（Life） ─── */
  { type: "video", category: "Life", date: "2015-01-01", source: "youtube", src: "https://www.youtube.com/embed/4pxY8dDh7aM?start=0", thumb: "https://img.youtube.com/vi/4pxY8dDh7aM/hqdefault.jpg", caption: "黑龙江大学 吴坚 再见时光 2015" },

  { type: "video", category: "Life", date: "2024-01-01", source: "drive", src: "https://drive.google.com/file/d/1cHCGFyLsAE9JoJch5Ks019G6KGGWH_or/preview", thumb: "https://drive.google.com/thumbnail?id=1cHCGFyLsAE9JoJch5Ks019G6KGGWH_or&sz=w500", caption: "Video from Google Drive", caption_zh: "来自 Google Drive 的视频" }
];
