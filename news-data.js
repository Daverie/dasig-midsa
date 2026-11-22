// Sample data used only when pages are opened from disk (file://). With server.py, the live news.json is used instead.
const MIDSA_NEWS = {
  categories: [
    { slug: 'announcements', name: 'Announcements' },
    { slug: 'events', name: 'Events' },
    { slug: 'community', name: 'Community' }
  ],
  articles: [
    { slug: 'welcome-back-scholars', title: 'Welcome back, scholars', category: 'announcements', cover: '', featured: true,
      publishedAt: '2026-11-05', author: 'MIDSA Editorial', excerpt: 'Orientation week is here. Here is what to expect and where to be.',
      body: 'Orientation week starts on Monday.\n\n## What to bring\n\nBring your **scholar ID** and a notebook.\n\nWe will see you there.' },
    { slug: 'peer-tutoring-sessions', title: 'Peer tutoring sessions open for the semester', category: 'community', cover: '', featured: false,
      publishedAt: '2026-10-03', author: 'MIDSA Academics', excerpt: 'Sign up for weekly review sessions led by senior scholars.',
      body: 'Peer tutoring is back.\n\nSessions run every week before exams.' },
    { slug: 'scholars-gathering', title: 'Scholars gathering this December', category: 'events', cover: '', featured: false,
      publishedAt: '2026-09-12', author: 'MIDSA Events', excerpt: 'Save the date for our end-of-year gathering.',
      body: 'Our annual gathering returns.\n\nDetails will follow on our official channels.' }
  ]
};
