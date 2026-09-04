import { AppShell } from "@/components/app-shell";
import { Dashboard } from "@/components/dashboard";

export default function DashboardLayout({children}:{children:React.ReactNode}) {
  return <AppShell><Dashboard/><div className="hidden">{children}</div></AppShell>;
}
