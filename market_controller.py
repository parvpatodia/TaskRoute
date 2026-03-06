from market_state import load_market_state, save_market_state, jitter_market, apply_shock


def main():
    state = load_market_state()

    print("Current market multipliers")
    for p, v in state["provider_multipliers"].items():
        print(p, v)

    print()
    print("1 jitter market")
    print("2 shock openai up 40 percent")
    print("3 shock replicate down 30 percent")
    print("4 reset market to 1.0")
    print()

    choice = input("Select: ").strip()

    if choice == "1":
        state = jitter_market(state, jitter=0.06)
        print("Applied jitter")

    elif choice == "2":
        state = apply_shock(state, "openai", 1.4)
        print("OpenAI shock applied")

    elif choice == "3":
        state = apply_shock(state, "replicate", 0.7)
        print("Replicate discount applied")

    elif choice == "4":
        for k in state["provider_multipliers"].keys():
            state["provider_multipliers"][k] = 1.0
        print("Reset market")

    else:
        print("No change")

    save_market_state(state)

    print()
    print("Updated market multipliers")
    for p, v in state["provider_multipliers"].items():
        print(p, v)


if __name__ == "__main__":
    main()