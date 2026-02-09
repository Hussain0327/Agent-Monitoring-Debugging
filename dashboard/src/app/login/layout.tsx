export default function LoginLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen items-center justify-center bg-[var(--background)]">
      <div className="noise-bg fixed inset-0 pointer-events-none" />
      {children}
    </div>
  );
}
