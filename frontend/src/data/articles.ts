export interface ArticleCategory {
  id: string
  label: string
}

export interface ArticleSection {
  heading: string
  paragraphs: string[]
}

export interface ArticleItem {
  id: number
  category: string
  title: string
  summary: string
  tags: string[]
  author: string
  publishedAt: string
  readingMinutes: number
  sections: ArticleSection[]
}

export const ARTICLE_CATEGORIES: ArticleCategory[] = [
  { id: 'all', label: '全部' },
  { id: 'emotion', label: '情绪与压力' },
  { id: 'sleep', label: '睡眠与放松' },
  { id: 'know', label: '认识困扰' },
  { id: 'relation', label: '人际与沟通' }
]

export const ARTICLES: ArticleItem[] = [
  {
    id: 1,
    category: 'sleep',
    title: '睡不好？从“睡眠卫生”开始调整',
    summary: '规律作息、光线与屏幕习惯，往往比强迫自己睡着更有效。本文介绍可操作的睡眠卫生要点。',
    tags: ['失眠', '作息', '科普'],
    author: '心理健康服务平台',
    publishedAt: '2026-03-12',
    readingMinutes: 6,
    sections: [
      {
        heading: '为什么先谈睡眠卫生',
        paragraphs: [
          '偶尔一两晚睡不好不必过度紧张，但若长期入睡困难、易醒或白天明显困倦，可以先把环境与习惯调整到更配合睡眠的状态。',
          '睡眠卫生不是药物，而是一组关于作息、环境与行为的日常策略，适合作为自我调节的起点。'
        ]
      },
      {
        heading: '你可以尝试的具体做法',
        paragraphs: [
          '尽量固定起床时间，即使前一晚睡得少，也避免白天长时间补觉，以免打乱节律。',
          '睡前一小时减少强光与刺激性内容；若必须用手机，可开启护眼模式并降低亮度。',
          '卧室以暗、静、凉为原则；床尽量只用来睡觉，减少在床上工作或刷剧。'
        ]
      }
    ]
  },
  {
    id: 2,
    category: 'know',
    title: '焦虑时，身体会发生什么？',
    summary: '心跳加快、肌肉紧绷、肠胃不适……焦虑常常写在身体上。了解机制有助于减少二次恐惧。',
    tags: ['焦虑', '身心反应', '科普'],
    author: '心理健康服务平台',
    publishedAt: '2026-03-08',
    readingMinutes: 5,
    sections: [
      {
        heading: '焦虑是一种生存反应',
        paragraphs: [
          '面对威胁时，身体会进入战斗或逃跑模式：交感神经兴奋，心率与呼吸加快，血液更多流向大肌肉群。',
          '当没有真实危险、身体却长期处于高唤醒状态，就可能表现为慢性焦虑或惊恐发作样的不适。'
        ]
      },
      {
        heading: '可以做的自我调节',
        paragraphs: [
          '缓慢延长呼气有助于激活副交感神经。',
          '把注意力带回当下环境，帮助神经系统降温。若症状频繁干扰生活，建议做更系统的专业评估。'
        ]
      }
    ]
  },
  {
    id: 3,
    category: 'emotion',
    title: '情绪低落时，可以试试这几步',
    summary: '情绪有起伏是正常的。这里整理一些温和、可执行的小步骤，帮助你度过难熬的几天。',
    tags: ['情绪', '自助', '抑郁情绪'],
    author: '心理健康服务平台',
    publishedAt: '2026-02-26',
    readingMinutes: 7,
    sections: [
      {
        heading: '先照顾身体的基本盘',
        paragraphs: [
          '在情绪低谷时，大脑容易把小事放大成做不到。可以把目标降到最小：喝一口水、吃一点东西、洗把脸、到窗边站两分钟。',
          '不必追求立刻好起来，而是今天多完成一件小事就算进步。'
        ]
      },
      {
        heading: '减少孤立感',
        paragraphs: [
          '若暂时不想倾诉，也可以给信任的人发一句今天有点累，或者参加低压力的线上/线下活动。',
          '若你发现自己完全回避社交超过两周，建议考虑专业支持。'
        ]
      }
    ]
  },
  {
    id: 4,
    category: 'relation',
    title: '和身边人谈边界：温和而清晰',
    summary: '边界不是冷漠，而是让关系可持续。如何用我开头表达需求，同时给对方台阶？',
    tags: ['人际关系', '沟通', '边界'],
    author: '心理健康服务平台',
    publishedAt: '2026-02-10',
    readingMinutes: 6,
    sections: [
      {
        heading: '什么是心理边界',
        paragraphs: [
          '边界包括你愿意在时间上付出多少、哪些话题不想讨论、哪些行为让你不舒服。清晰边界能减少委屈与爆发式争吵。'
        ]
      },
      {
        heading: '表达公式示例',
        paragraphs: [
          '“我”陈述：描述事实 + 你的感受 + 具体请求。例如：你这周三次临时改时间，我会有点焦虑；下次能否提前一天告诉我？',
          '少用“你总是”“你从来不”，把注意力放在具体事件与影响上。'
        ]
      }
    ]
  }
]

export function getCategoryLabel(categoryId: string) {
  return ARTICLE_CATEGORIES.find((item) => item.id === categoryId)?.label || categoryId
}

export function getArticleById(id: number) {
  return ARTICLES.find((item) => item.id === id)
}
