import React from 'react'
import { Link } from 'react-router-dom'
import { useI18n } from '../../../i18n/useI18n'

export const LoginPage: React.FC = () => {
  const { t } = useI18n()

  return (
    <div className="relative min-h-screen flex items-center justify-center p-4 bg-[linear-gradient(180deg,rgba(255,255,255,0.98)_0%,rgba(250,252,255,0.96)_52%,rgba(246,249,253,0.95)_100%)]">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-64 bg-[radial-gradient(circle_at_top,rgba(217,235,255,0.45),transparent_70%)]" />

      <div className="relative w-full max-w-sm flex flex-col gap-6 rounded-[28px] bg-[rgba(255,255,255,0.82)] backdrop-blur-xl border border-white/80 ring-1 ring-black/[0.03] p-8 shadow-[0_12px_32px_rgba(15,23,42,0.05)]">
        <div className="absolute inset-0 rounded-[28px] pointer-events-none bg-[linear-gradient(180deg,rgba(255,255,255,0.28),rgba(255,255,255,0.06)_50%,transparent)]" />

        <div className="relative text-center">
          <div className="text-[28px] font-semibold text-slate-900">
            小星
          </div>
          <div className="text-sm text-slate-500 mt-2">
            系统维护中
          </div>
        </div>

        <div className="relative rounded-2xl border border-slate-200/70 bg-white/60 px-4 py-5 text-center shadow-[inset_0_1px_0_rgba(255,255,255,0.85)]">
          <div className="text-base font-medium text-slate-900">
            登录入口暂时关闭
          </div>
          <div className="mt-2 text-sm leading-6 text-slate-500">
            Xiaoxing AI 正在进行系统维护，服务恢复后将重新开放登录。感谢你的理解。
          </div>
        </div>

        <div className="flex items-center justify-center gap-4 text-xs text-slate-500">
          <Link to="/privacy" className="hover:text-slate-900 transition-colors">
            {t('nav.privacy')}
          </Link>
          <span className="opacity-30">·</span>
          <Link to="/terms" className="hover:text-slate-900 transition-colors">
            {t('nav.terms')}
          </Link>
        </div>
      </div>
    </div>
  )
}
