export default function Sidebar() {
  return (
    <aside className="w-64 border-r bg-white h-screen p-4">
      <h2 className="font-bold mb-6">
        MENU
      </h2>

      <nav className="space-y-2">
        <button className="w-full text-left rounded-lg p-2 hover:bg-gray-100">
          Dashboard
        </button>

        <button className="w-full text-left rounded-lg p-2 hover:bg-gray-100">
          Văn bản
        </button>

        <button className="w-full text-left rounded-lg p-2 hover:bg-gray-100">
          AI
        </button>

        <button className="w-full text-left rounded-lg p-2 hover:bg-gray-100">
          Cài đặt
        </button>
      </nav>
    </aside>
  );
}