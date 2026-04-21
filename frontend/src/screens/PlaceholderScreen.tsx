type Props = {
  title: string;
  onBack: () => void;
};

function PlaceholderScreen({ title, onBack }: Props) {
  return (
    <div className="selection-panel">
      <button type="button" className="selection-button" onClick={onBack}>
        ← Tornar
      </button>

      <h2 className="section-title">{title}</h2>
      <p className="selection-text">Funcionalitat en desenvolupament</p>
    </div>
  );
}

export default PlaceholderScreen;