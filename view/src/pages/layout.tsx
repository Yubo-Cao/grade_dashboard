import Header from "@/components/Header";

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="flex flex-col items-center h-[100vh] w-[100vw] p-4">
            <Header />
            <div className="p-4 md:px-8 lg:px-12 lg:max-w-7xl w-full h-full">
                {children}
            </div>
        </div>
    );
}
