#!/usr/bin/python
import re
from types import SimpleNamespace as ns
import ledutil

def format_key(key):
    result = re.sub("[^a-z]+", "", key.lower())
    result = re.sub("_", "-", result)
    return result

def format_value(value):
    if isinstance(value, bool): return "on" if value else "off"
    if isinstance(value, int):  return str(value)
    if isinstance(value, list): return ",".join(map(str, value))
    else:
        raise TypeError(
            "Value should be int, bool, or list, " \
            f"not {type(value).__name__}"
        )

def format_flag(flag, value):
    result = re.sub("[^a-z]+", "", flag.lower())
    result = re.sub("_", "-", result)
    symbol = ["!", "&"][value]
    return f"{symbol}{result}"

def strip_symbol(value, symbol):
    if isinstance(symbol, tuple) or isinstance(symbol, list):
        v = value
        for s in symbol:
            v = strip_symbol(v, s)
        return v
    if isinstance(value, str) and value and value[0:len(symbol)] == symbol:
        return value[len(symbol):]
    return value

class Message:
    def __init__(self,
                 type,
                 subtype="",
                 objects=set(),
                 values={},
                 flags=[],
                 freetext=""
    ):
        self._type = ""
        self._subtype = ""
        self._objects = objects
        self._values = {}
        self._flags = {}
        self._freetext = ""

        self.type(type)
        self.subtype(subtype)
        self.set_values(**values)
        self.add_flags(flags)
        self.freetext(freetext)

    def __str__(self):
        return "".join([
            self.type(),
            self.subtype(),
            self.format_objects(),
            self.format_values(),
            self.format_flags(),
            self.freetext(),
            "\n"
       ])

    def __repr__(self):
        return f"<{self.type()}{self.subtype()} message>"

    def __getitem__(self, item):
        if item[0] in "&!":
            symbol, flag = item[0], item[1:]
            has_flag = flag in self._flags
            value = has_flag and self._flags[flag]

            if symbol == "&":
                return value
            if symbol == "!" and has_flag:
                return self._flags[flag] is False
            if symbol == "!" and not has_flag:
                return True
        return self._values[item]

    def __contains__(self, item):
        if item[0] in ("&", "!"):
            return item[1:] in self._flags
        return item in self._values

    def report(self):
        title = f"{self.prefixes()} message"
        result = [f"[ {title} ]"]
        if self._objects:
            result.append(f"  Objects:{self.format_objects()}")
        if self._values:
            result.append(f"  Values:")
            for k, v in self._values.items():
                result.append(f"    {format_key(k)}={format_value(v)}")
        if self._flags:
            result.append(f"  Flags:{self.format_flags()}")
        if self._freetext:
            result.append(f"  {self.freetext()}")
        result.append(f"--{'-' * len(title)}--")
        return "\n".join(result)

    def brief(self):
        objects = self.format_objects()
        if objects:
            objects = f" {objects}"
        return f"[ {self.type()}{self.subtype()}{objects} ]{self.freetext()}"

    def type(self, *value):
        if value:
            self._type = strip_symbol(value[0], ":")
            return self
        return f":{self._type}" if self._type else ""

    def subtype(self, *value):
        if value:
            self._subtype = strip_symbol(value[0], ":")
            return self
        return f":{self._subtype}" if self._subtype else ""

    def prefixes(self):
        return f"{self.type()}{self.subtype()}"

    def args(self):
        return "".join([
            self.format_objects(),
            self.format_values(),
            self.format_flags()
        ])

    def kwargs(self):
        for k, v in self._values.items():
            key = re.sub("-", "_", k)
            pairs[key] = v
        for f, v in self._flags.items():
            flag = re.sub("-", "_", f)
            pairs[flag] = v
        return pairs

    def objects(self):
        return sorted(self._objects)

    def add_objects(self, *objects):
        for obj in objects:
            self._objects.add(obj)
        return self

    def format_objects(self):
        if not self._objects:   return ""
        numbers = sorted(self._objects)
        result = []
        start = end = numbers[0]
        for num in numbers[1:]:
            if num - end == 1:
                end = num
            else:
                if start == end:
                    result.append(str(start))
                else:
                    result.append(f"{start}-{end}")
                start = end = num
        if start == end:
            result.append(str(start))
        else:
            result.append(f"{start}-{end}")
        return "\x20#" + ",".join(result)

    def set_values(self, **kv):
        for k, v in kv.items():
            self._values[k] = v
        return self
    set_value = set_values

    def format_values(self):
        return "".join([
            f" {format_key(k)}={format_value(v)}"
            for k, v in self._values.items()
        ])

    def add_flags(self, flags, value=None):
        for flag in flags:
            v = value
            if v is None:
                if flag[0] == "&": v = True
                if flag[0] == "!": v = False
            if v is None:
                v = True
            f = strip_symbol(flag, ("&", "!"))
            self._flags[f] = v
        return self

    def format_flags(self):
        return "".join([
            f" {format_flag(f, v)}"
            for f, v in self._flags.items()
        ])

    def freetext(self, *value):
        if value:
            self._freetext = strip_symbol(value[0], "//")
            return self
        return f" //{self._freetext}" if self._freetext else ""

    def validate(self,
                 require_objects=False,
                 required_values=[],
                 accepted_values=[],
                 accepted_flags=[],
                 allow_unneeded_objects=False,
                 allow_other_values=False,
                 allow_other_flags=False
    ):
        errors = []

        has_objects = len(self._objects) > 0
        if require_objects and not has_objects:
            errors.append("missing required objects")
        elif has_objects and not require_objects and forbid_unneeded_objects:
            errors.append("unneeded objects given")

        missing_values = set()
        for k in required_values:
            if not k in self._values:
                missing_values.add(f"{k}=")
        if missing_values:
            errors.append("".join([
                "missing required key/value pair(s) ",
                ledutil.oxford_comma(sorted(missing_values))
            ]))

        if not allow_other_values:
            other_values = set()
            for k in self._values:
                if k not in required_values \
                and k not in accepted_values:
                    other_values.add(f"{k}=")
            if other_values:
                errors.append("".join([
                    "unknown key/value pair(s) ",
                    ledutil.oxford_comma(list(other_values))
                ]))

        if not allow_other_flags:
            accepted_flags = set(
                strip_symbol(f, ("&", "!"))
                for f in accepted_flags
            )
            other_flags = set()
            for f in self._flags:
                if f not in accepted_flags:
                    other_flags.add(format_flag(f, self._flags[f]))
            if other_flags:
                errors.append("".join([
                    "unknown flag(s) ",
                    ledutil.oxford_comma(list(other_flags))
                ]))

        if errors:
            raise type(self).ValidationError(
                f"validation error in {self.type()}{self.subtype()} message - " \
                + ledutil.oxford_comma(errors)
            )

    class ValidationError(Exception):
        pass

class MessageParser:
    T_PREFIX = re.compile(":([a-z-]+)")
    T_EOL = re.compile("[\x0D\x0A]+")
    T_OBJECTS = re.compile(" +#([0-9]+(?:-[0-9]+)?(?:,[0-9]+(?:-[0-9]+)?)*)")
    T_KEY = re.compile(" +([a-z-]+)=")
    T_LIST = re.compile("([0-9]+,[0-9]+(?:,[0-9]+)*)")
    T_TOGGLE = re.compile("(on|off)")
    T_NUMBER = re.compile("([0-9]+)")
    T_FLAG = re.compile(" +([&!][a-z-]+)")
    T_FREETEXT = re.compile(" +//([^\x0D\x0A]+)")

    TOKENS = {
        "PREFIX": T_PREFIX,
        "OBJECTS": T_OBJECTS,
        "KEY": T_KEY,
        "LIST": T_LIST,
        "TOGGLE": T_TOGGLE,
        "NUMBER": T_NUMBER,
        "FLAG": T_FLAG,
        "FREETEXT": T_FREETEXT,
        "EOL": T_EOL
    }

    def __init__(self):
        self._line = ""
        self._tokens = []
        self._message = None

        self._parsed = None

    def _truncate(self, line, length=5):
        dots1 = "..." if len(line) < len(self._line) else ""
        dots2 = "..." if len(line) > length else ""
        return f"{dots1}'{line[0:length]}'{dots2}"

    def analyze(self, line):
        result = []
        self._line = line
        self._message = None

        dirty = True
        while dirty and len(line):
            dirty = False
            for token_type, pattern in self.TOKENS.copy().items():
                match = pattern.match(line)
                if match:
                    result.append(ns(
                        token_type=token_type,
                        value=match[1]
                    ))
                    line = line[match.end():]
                    dirty = True
                    break

        if len(line):
            raise type(self).ParseError(
                "unrecognized input " \
                f"{self._truncate(line)} in " \
                f"'{self._line}'"
            )

        self._tokens = result
        return result


    def parse(self, line):
        self.analyze(line)

        type = self.accept("PREFIX", required=True).value
        subtype = self.accept("PREFIX")
        subtype = subtype.value if subtype else ""
        objects = set()
        values = {}
        flags = []

        ok = True
        while ok:
            if self.parse_objects():
                objects |= self._parsed
                continue

            if self.parse_keyvalue_pair():
                values[self._parsed[0]] = self._parsed[1]
                continue

            if self.parse_flag():
                flags.append(self._parsed)
                continue

            ok = False

        freetext = self.parse_freetext()

        return Message(
            type=type,
            subtype=subtype,
            objects=sorted(objects),
            values=values,
            flags=flags,
            freetext=freetext
        )

    def parse_objects(self):
        result = set()
        o = self.accept("OBJECTS")
        if o:
            for member in o.value.split(","):
                if "-" in member:
                    start, end = member.split("-")
                    for i in range(int(start), int(end)+1):
                        result.add(i)
                else:
                    result.add(int(member))
            self._parsed = result
            return True
        return False

    def parse_keyvalue_pair(self):
        k = self.accept("KEY")
        if k:
            k = k.value
            v = self.accept("LIST", "TOGGLE", "NUMBER", required=True)
            if v.token_type == "LIST":
                v = [int(i) for i in v.value.split(",")]
            elif v.token_type == "TOGGLE":
                v = v.value == "on"
            elif v.token_type == "NUMBER":
                v = int(v.value)
            self._parsed = (k, v)
            return True
        return False

    def parse_flag(self):
        f = self.accept("FLAG")
        if f:
            self._parsed = f.value
            return True
        return False

    def parse_freetext(self):
        f = self.accept("FREETEXT")
        if f:
            return f.value
        return ""

    def accept(self, *token_types, required=False, shift=True):
        if self._tokens and self._tokens[0].token_type in token_types:
            result = self._tokens[0]
            shift and self._tokens.pop(0)
            return result
        if required:
            expected = ledutil.oxford_comma(token_types, and_="or")
            raise type(self).ParseError(
                f"expected {expected} " \
                f"but got {self._tokens[0].token_type}"
            )
        return None

    class ParseError(Exception):
        pass

