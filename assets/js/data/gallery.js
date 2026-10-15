const galleryData = [
  { type: "photo", source: "local", src: "assets/img/gallery/photo1.jpg", caption: "Jian Wu", caption_zh: "吴坚" },
  // 下面几张暂时没有实际文件，先注释掉，以后补上照片再取消注释
  // { type: "photo", source: "local", src: "assets/img/gallery/photo2.jpg", caption: "Lab life", caption_zh: "实验室日常" },
  // { type: "photo", source: "local", src: "assets/img/gallery/photo3.jpg", caption: "Conference trip", caption_zh: "会议之行" },
  // { type: "photo", source: "local", src: "assets/img/gallery/photo4.jpg", caption: "Nature walk", caption_zh: "户外漫步" },

  // 照片（Google Drive 来源，保留原有条目）
  { type: "photo", source: "drive", src: "https://drive.google.com/thumbnail?id=1p6jXfQAw9Mn75sHmMVZ9GIDLfvi2ttMA&sz=w1000", caption: "Photo from Google Drive", caption_zh: "谷歌云盘照片" },

  // 视频（Google Drive 来源，保留原有条目）
  { type: "video", source: "drive", src: "https://drive.google.com/file/d/1cHCGFyLsAE9JoJch5Ks019G6KGGWH_or/preview", thumb: "https://drive.google.com/thumbnail?id=1cHCGFyLsAE9JoJch5Ks019G6KGGWH_or&sz=w500", caption: "Video from Google Drive", caption_zh: "谷歌云盘视频" },

  /* ─── 新增：YouTube 视频 ─── */
  {
    type: "video",
    source: "youtube",
    src: "https://www.youtube.com/embed/4pxY8dDh7aM?start=0",
    thumb: "https://img.youtube.com/vi/4pxY8dDh7aM/hqdefault.jpg",
    caption: "黑龙江大学 吴坚 再见时光 2015"
  },

  /* ─── 新增：本地机构活动照片（assets/img/gallery/） ─── */
  { type: "photo", source: "local", src: "assets/img/gallery/2024-03-05-CIGL_party-合照.jpeg", caption: "CIGL Party · 2024-03-05", caption_zh: "CIGL 派对 · 2024-03-05" },

  { type: "photo", source: "local", src: "assets/img/gallery/2024-12-14--单独Soni.jpeg", caption: "与 Prof. Soni Savai Pullamsetti 合影 · 2024-12-14" },

  { type: "photo", source: "local", src: "assets/img/gallery/2024-12-14-合照2-X.jpeg", caption: "团队合照 · 2024-12-14" },

  { type: "photo", source: "local", src: "assets/img/gallery/CPI会议.jpeg", caption: "CPI 会议" },

  { type: "photo", source: "local", src: "assets/img/gallery/CRC Retreat 2025.jpg", caption: "CRC Retreat 2025", caption_zh: "CRC 静修会 · 2025" },

  { type: "photo", source: "local", src: "assets/img/gallery/DataLung 2026 合照.jpeg", caption: "DataLung 2026 合照" },

  { type: "photo", source: "local", src: "assets/img/gallery/DZL 2024 合照.jpg", caption: "DZL 2024 合照" },

  { type: "photo", source: "local", src: "assets/img/gallery/DZL 2025合照.jpg", caption: "DZL 2025 合照" },

  { type: "photo", source: "local", src: "assets/img/gallery/DZL2026-合照.jpg", caption: "DZL 2026 合照" },

  { type: "photo", source: "local", src: "assets/img/gallery/ILH Symposium 2025.jpeg", caption: "ILH Symposium 2025", caption_zh: "ILH 研讨会 · 2025" },

  { type: "photo", source: "local", src: "assets/img/gallery/Image from CPI 2.0 合照.png", caption: "CPI 2.0 团队合照" }
];