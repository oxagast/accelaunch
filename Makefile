# Define where to install files
PREFIX=/usr/local
LIBDIR=$(PREFIX)/lib
CONFDIR=$(PREFIX)/etc
UID = id -u
RAISE = sudo make
.PHONY: uninstall deinstall clean

# Install target
install: accelaunch.py
    ifneq ($(shell $(UID)), 0)
	$(RAISE) $@
    else
	mkdir -p $(LIBDIR)/accelaunch
	cp accelaunch.py $(LIBDIR)/accelaunch/accelaunch.py
	mkdir -p $(CONFDIR)/accelaunch
	cp config.yaml.example $(CONFDIR)/accelaunch/config.yaml.example
	chown root $(LIBDIR)/accelaunch/accelaunch.py
	chmod a+rx,u+rwx $(LIBDIR)/accelaunch/accelaunch.py
	cp accelaunch.service /etc/systemd/system/multi-user.target.wants/accelaunch.service
    endif

# Remove the installed target
deinstall:
    ifneq ($(shell $(UID)), 0)
	$(RAISE) $@
    else
	rm -rf $(LIBDIR)/accelaunch
	rm -f /etc/systemd/system/multi-user.target.wants/accelaunch.service
    endif

uninstall: deinstall
