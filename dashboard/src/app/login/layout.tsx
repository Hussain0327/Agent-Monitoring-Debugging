export default function LoginLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen items-center justify-center bg-[var(--background)]">
      {children}
    </div>
  );
}
