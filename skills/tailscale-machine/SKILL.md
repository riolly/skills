---
name: tailscale-machine
description: Add a machine to a tailnet and get it connecting directly, or diagnose why two machines are slow or relayed. Use when setting up a new laptop, desktop or server on Tailscale, or when `tailscale ping` shows DERP, a machine shows "relay", or remote access feels slow.
---

# Tailscale machine setup

Runbook for adding a machine to a tailnet and checking how it connects.

## Private notes

Machine names, addresses and ISP details belong in `~/.config/tailscale-machine/network.md`, never in this skill or in any repo. Read that file first if it exists. Treat its values as a starting point, because addresses change. Create it if it's missing, and update it after each setup.

## Add a new machine

1. **Install and sign in.** Use the same account as the other machines. On Linux: `curl -fsSL https://tailscale.com/install.sh | sh`, then `sudo tailscale up`.
2. **Put the CLI on PATH.** On macOS the app may not do this, and the binary is at `/Applications/Tailscale.app/Contents/MacOS/Tailscale`. Use the app's CLI integration setting or a symlink. Scripts that run plain `tailscale` otherwise behave as if Tailscale isn't installed.
3. **Turn on IPv6.**
   - macOS: `networksetup -setv6automatic Wi-Fi`.
   - Linux: check with `ip -6 addr show scope global`.
4. **Run `tailscale netcheck`.** Note `UDP`, `IPv6`, `MappingVariesByDestIP` and `PortMapping`.
5. **Confirm both machines are online.** Run `tailscale status`. An `offline` peer makes every other test meaningless, and its LAN address will not answer ping.
6. **Test on the same network.** Run `tailscale ping <peer>`. Expect a LAN address.
7. **Test from another network.** Put one machine on a phone hotspot and repeat. See the table below for what the result means.
8. **Update the private notes** with the new machine.

## Reading `tailscale ping`

| Output | Meaning | Action |
|---|---|---|
| `via <lan-ip>:port` | Direct on the LAN | Done |
| `via [<ipv6>]:port` | Direct over IPv6 | Done |
| `via <public-ip>:port` | Direct over IPv4 | Done |
| `via DERP(<region>)` on the same LAN | Something is wrong | Check both are on the same subnet, and look for AP or guest isolation |
| `via DERP(<region>)` across networks | Relayed, but working | Leave it unless it's too slow |
| `direct connection not established` | Stopped after 10 relayed pings | Same as the row above |

Add `-c 6 --until-direct=false` to get several samples. Do not judge from one ping: the first is often slow, and Wi-Fi can spike to 100ms when most pings are under 10ms.

## Why a direct connection fails

- **Hard NAT on one side.** `MappingVariesByDestIP: true` means the NAT picks a new port per destination, which makes direct IPv4 unlikely. Hard NAT on both sides almost always relays.
- **No IPv6 on one side.** Both ends need it. Many hotspots give IPv4 only, so a machine with IPv6 can't be reached from them over IPv6.
- **CGNAT.** The ISP holds the public IP, so nothing on the local router can open a port.

## Check for CGNAT

Works without the router login:

```sh
curl -4 -s https://ifconfig.me
traceroute -n -m 8 -q 1 -w 2 <that-ip>
```

If the trace ends at hop 1, the router owns the public IP, so forwarding UDP 41641 can work. If it continues past the router, something upstream holds the IP and forwarding is useless.

To confirm, read the WAN IP on the router's status page. A private address, or `100.64` to `100.127`, means CGNAT.

## If the relay is too slow

Relays are fine for terminal and file work. Large transfers suffer. Try these in order:

1. **IPv6 on the phone.** Set the APN protocol to `IPv4/IPv6`, restart the hotspot, and run `tailscale netcheck`. Depends on the carrier and on the router's IPv6 firewall.
2. **Public IPv4 from the ISP.** Forward UDP 41641 to the target machine and reserve its LAN IP in DHCP. On a Mac, turn off Private Wi-Fi Address for that network first, or the reservation may stop matching.
3. **VPS relay.** Helps transfer speed. A VPS near the DERP region won't improve latency, so pick somewhere closer.

## Mistakes to avoid

- Do not assume a LAN address belongs to the machine you are on. An address that doesn't answer may be another machine that's offline. Run `tailscale status` and `arp -an` to see who owns it.
- Do not credit IPv6 for a direct LAN link. Read the address in the `tailscale ping` output.
- Do not forward a port before checking for CGNAT.
- Do not log in to a router with guessed or default credentials. Ask the owner to read the page.
- Do not put addresses from this work in a public repo.
