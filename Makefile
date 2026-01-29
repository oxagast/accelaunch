# Define where to install files
PREFIX=/usr/local
LIBDIR=$(PREFIX)/lib
MANDIR=$(PREFIX)/man/man8
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
	mkdir -p $(MANDIR)
	gzip accelaunch.8 -c > $(MANDIR)/accelaunch.8.gz
	systemctl daemon-reload
	@echo
	@echo "Don't forget to edit /usr/local/etc/accelaunch/config.yaml!"
	@echo "Run: systemctl enable accelaunch after editing your config before next boot!"
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
