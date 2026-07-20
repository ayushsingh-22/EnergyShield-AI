// Renders the commodity selection control for switching between crude oil, LNG, coal, fertilizers, and critical minerals.
export default function CommoditySelector({ commodities, selected, onSelect }) {
  if (!commodities?.length) return null

  return (
    <div className="component component-commodity-selector">
      {commodities.map((commodity) => (
        <button
          key={commodity.commodity_type}
          type="button"
          className={
            commodity.commodity_type === selected
              ? 'commodity-chip commodity-chip--active'
              : 'commodity-chip'
          }
          onClick={() => onSelect?.(commodity.commodity_type)}
        >
          {commodity.display_name}
          <span className="commodity-chip__unit">{commodity.unit}</span>
        </button>
      ))}
    </div>
  )
}
