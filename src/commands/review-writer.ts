// NTCode Review Writer Command - 全自动综述写作
// 用法: ntcode --review-writer "主题" [--journal briefings|nature|cell|science]

import * as path from 'path'
import * as os from 'os'
import { ReviewWriter, ReviewConfig } from '../services/reviewWriter.js'
import { REVIEW_WRITER_PREFIX, REVIEW_WRITER_SUFFIX } from '../constants/reviewSystemPrompt.js'

export interface ReviewWriterArgs {
  topic: string
  journal?: 'briefings' | 'nature' | 'cell' | 'science'
  maxIterations?: number
  outputDir?: string
}

export async function executeReviewWriter(args: ReviewWriterArgs): Promise<void> {
  const {
    topic,
    journal = 'briefings',
    maxIterations = 3,
    outputDir
  } = args

  // 生成输出目录
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
  const finalOutputDir = outputDir || path.join(
    os.homedir(),
    'Desktop',
    'ntcode',
    'review-system',
    'output',
    `review_${timestamp}`
  )

  // 创建配置
  const config: ReviewConfig = {
    topic,
    journal,
    maxIterations,
    outputDir: finalOutputDir
  }

  // 创建 Review Writer 实例
  const writer = new ReviewWriter(config)

  try {
    // 执行综述写作流程
    const pdfPath = await writer.run()

    console.log('\n' + '='.repeat(60))
    console.log('✅ 综述写作完成！')
    console.log(`PDF: ${pdfPath}`)
    console.log('='.repeat(60))
  } catch (error) {
    console.error('\n❌ 综述写作失败:', error)
    throw error
  }
}

// 解析命令行参数
export function parseReviewWriterArgs(args: string[]): ReviewWriterArgs {
  if (args.length === 0) {
    throw new Error('请提供综述主题，例如: ntcode --review-writer "单细胞转录组"')
  }

  const topic = args[0]
  let journal: 'briefings' | 'nature' | 'cell' | 'science' = 'briefings'
  let maxIterations = 3
  let outputDir: string | undefined

  for (let i = 1; i < args.length; i++) {
    switch (args[i]) {
      case '--journal':
        journal = args[++i] as any
        break
      case '--max-iterations':
        maxIterations = parseInt(args[++i])
        break
      case '--output':
        outputDir = args[++i]
        break
    }
  }

  return { topic, journal, maxIterations, outputDir }
}

// 导出系统提示词（用于注入到 NTCode 会话中）
export function getReviewWriterSystemPrompt(topic: string): string {
  return REVIEW_WRITER_PREFIX + `\n\n## 当前综述主题\n\n${topic}\n\n` + REVIEW_WRITER_SUFFIX
}
