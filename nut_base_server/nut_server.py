"""Base nut server."""

import asyncio

from nut_definitions import NUT_COMMANDS_RE, NutCommand, NutError, build_nut_error

from .adapter.base_adapter import BaseAdapter
from .exceptions import DisconnectRequestedException


class NutServer:
    def __init__(self, adapter: BaseAdapter, host: str = "0.0.0.0", port: int = 3493):
        self.adapter = adapter
        self.host = host
        self.port = port

    async def start(self):
        server = await asyncio.start_server(
            self._handle_connection, self.host, self.port
        )
        async with server:
            await server.serve_forever()

    async def _handle_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        print("New connection")
        while True:
            try:
                buffer = await reader.readuntil()
                data = buffer.decode()

                if not data:
                    break

                print(f"-> {repr(data)}")
                result = await self._handle_command(data)
                print(f"<- {repr(result)}")
                writer.write(f"{result}\n".encode())
            except DisconnectRequestedException:
                print("Client disconnected")
                break
            except:
                print("Error")
                break

        writer.close()

    async def _handle_command(self, command: str) -> str:
        command = command.strip()
        regexed = NUT_COMMANDS_RE.match(command)

        if regexed is None:
            return build_nut_error(NutError.UnknownCommand)

        cw = regexed.group("cw")
        ca = regexed.group("ca")

        if cw is None and ca is None:
            return build_nut_error(NutError.UnknownCommand)

        # Extract args from the full command string — the regex args group
        # only captures [A-Za-z0-9]+ so it misses dots and multi-word args
        # (e.g. "GET VAR powerstation ups.status" would fail via regex).
        matched_cmd = cw if cw is not None else ca
        args = command[len(matched_cmd):].strip() or None

        if cw is not None:
            parsed = NutCommand(cw)

        if ca is not None:
            parsed = NutCommand(ca)
            if args is None and parsed not in (NutCommand.Username, NutCommand.Password):
                return build_nut_error(NutError.UnknownCommand)

        match (parsed):
            case NutCommand.GetNumlogins:
                return self._get_numlogins(args)
            case NutCommand.GetUpsdesc:
                return self._get_upsdesc(args)
            case NutCommand.GetVar:
                return await self._get_var(args)
            case NutCommand.GetType:
                return await self._get_type(args)
            case NutCommand.ListUps:
                return self._list_ups()
            case NutCommand.ListVar:
                return await self._list_var(args)
            case NutCommand.Logout:
                raise DisconnectRequestedException()
            case NutCommand.Username:
                return "OK"
            case NutCommand.Password:
                return "OK"
            case NutCommand.Login:
                return "OK"
            case NutCommand.NetVersion:
                return "NETVER 1.2"

        return build_nut_error(NutError.FeatureNotSupported)

    def _get_numlogins(self, args: str) -> str:
        if args != self.adapter.name:
            return build_nut_error(NutError.UnknownUps)

        return "\n".join(
            [
                f"NUMLOGINS {args} {str(self.adapter.numlogins())}",
            ]
        )

    def _get_upsdesc(self, args: str) -> str:
        if args != self.adapter.name:
            return build_nut_error(NutError.UnknownUps)

        return "\n".join(
            [
                f'UPSDESC {args} "{self.adapter.description}"',
            ]
        )

    async def _get_var(self, args: str) -> str:
        splitted = args.split(" ")

        if len(splitted) != 2:
            return build_nut_error(NutError.InvalidArgument)

        if splitted[0] != self.adapter.name:
            return build_nut_error(NutError.UnknownUps)

        value = await self.adapter.get_variable_value(splitted[1])

        if value is None:
            return build_nut_error(NutError.VarNotSupported)

        return f'VAR {self.adapter.name} {splitted[1]} "{value}"'

    async def _get_type(self, args: str) -> str:
        splitted = args.split(" ")

        if len(splitted) != 2:
            return build_nut_error(NutError.InvalidArgument)

        if splitted[0] != self.adapter.name:
            return build_nut_error(NutError.UnknownUps)

        value = await self.adapter.get_variable_value(splitted[1])
        vType = await self.adapter.get_variable_type(splitted[1])

        if value is None or vType is None:
            return build_nut_error(NutError.VarNotSupported)

        return f'VAR {self.adapter.name} {splitted[1]} "{vType}"'

    def _list_ups(self) -> str:
        return "\n".join(
            [
                "BEGIN LIST UPS",
                f'UPS {self.adapter.name} "{self.adapter.description}"',
                "END LIST UPS",
            ]
        )

    async def _build_var_list(self) -> list[str]:
        variables = await self.adapter.get_all_variables()

        return [f'VAR {self.adapter.name} {v.name} "{v.value}"' for v in variables]

    async def _list_var(self, args: str) -> str:
        if args != self.adapter.name:
            return build_nut_error(NutError.UnknownUps)

        variables = await self._build_var_list()

        return "\n".join(
            [f"BEGIN LIST VAR {args}"] + variables + [f"END LIST VAR {args}"]
        )
