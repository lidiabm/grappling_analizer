import ArrowLeftIcon from "../icons/ArrowLeftIcon"
type Props = {
  title: string;
  onBack: () => void;
};

function PlaceholderScreen({ title, onBack }: Props) {
  return (
    <div className="selection-panel">
      <button type="button" className="selection-button" onClick={onBack}>
        <ArrowLeftIcon size={20} />
      </button>

      <h2 className="section-title">{title}</h2>
      <p className="selection-text">Funcionalitat en desenvolupament</p>
    </div>
  );
}

export default PlaceholderScreen;