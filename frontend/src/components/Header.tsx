import "./Header.css";

type HeaderProps = {
  onGoHome: () => void;
};

function Header({ onGoHome }: HeaderProps) {
  return (
    <header className="topbar">
      <button
        type="button"
        className="topbar-brand"
        onClick={onGoHome}
      >
        Analitzador de Grappling
      </button>
    </header>
  );
}

export default Header;