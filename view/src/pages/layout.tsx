import Header from "@/components/Header";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center h-fill w-[100vw] p-4">
      <Header />
      <div className="p-4 md:px-8 lg:px-12 lg:max-w-6xl w-full">{children}</div>
    </div>
  );
}
